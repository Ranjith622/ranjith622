"""
Orders App - Views
===================
Session-based cart, checkout, and order confirmation.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from products.models import Product
from .models import Order, OrderItem


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _get_cart(request):
    """Return cart dict from session, always a dict keyed by product-id string."""
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def _cart_totals(cart):
    """Return (items list with product objects, subtotal)."""
    items, subtotal = [], 0
    for pid, data in cart.items():
        try:
            product = Product.objects.get(pk=int(pid), is_active=True)
            qty = data['quantity']
            line = qty * float(product.price)
            subtotal += line
            items.append({'product': product, 'quantity': qty, 'subtotal': round(line, 2)})
        except Product.DoesNotExist:
            pass
    return items, round(subtotal, 2)


# ─────────────────────────────────────────────
#  Cart Views
# ─────────────────────────────────────────────

def cart_view(request):
    """Display the shopping cart page."""
    cart = _get_cart(request)
    items, subtotal = _cart_totals(cart)
    shipping = 0 if subtotal >= 500 else 40
    total = subtotal + shipping
    context = {
        'cart_items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def cart_add(request):
    """Add or update a product in the cart (AJAX or form POST)."""
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    product_id = str(data.get('product_id'))
    quantity   = int(data.get('quantity', 1))

    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if quantity < 1 or quantity > product.stock:
        return JsonResponse({'success': False, 'message': 'Invalid quantity.'}, status=400)

    cart = _get_cart(request)
    if product_id in cart:
        cart[product_id]['quantity'] = min(cart[product_id]['quantity'] + quantity, product.stock)
    else:
        cart[product_id] = {'quantity': quantity, 'price': str(product.price)}

    _save_cart(request, cart)
    total_count = sum(v['quantity'] for v in cart.values())

    return JsonResponse({
        'success': True,
        'message': f'"{product.name}" added to cart!',
        'cart_count': total_count,
    })


@require_POST
def cart_update(request):
    """Update quantity of an item in the cart (AJAX)."""
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    product_id = str(data.get('product_id'))
    quantity   = int(data.get('quantity', 1))

    cart = _get_cart(request)
    if product_id in cart:
        if quantity <= 0:
            del cart[product_id]
        else:
            try:
                product = Product.objects.get(pk=product_id)
                cart[product_id]['quantity'] = min(quantity, product.stock)
            except Product.DoesNotExist:
                del cart[product_id]
    _save_cart(request, cart)

    # Recalculate totals for AJAX response
    items, subtotal = _cart_totals(cart)
    shipping = 0 if subtotal >= 500 else 40
    total = subtotal + shipping
    total_count = sum(v['quantity'] for v in cart.values())

    return JsonResponse({
        'success': True,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'cart_count': total_count,
    })


@require_POST
def cart_remove(request):
    """Remove an item from the cart (AJAX)."""
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    product_id = str(data.get('product_id'))
    cart = _get_cart(request)
    cart.pop(product_id, None)
    _save_cart(request, cart)

    items, subtotal = _cart_totals(cart)
    shipping = 0 if subtotal >= 500 else 40
    total_count = sum(v['quantity'] for v in cart.values())

    return JsonResponse({
        'success': True,
        'subtotal': subtotal,
        'shipping': 0 if subtotal >= 500 else 40,
        'total': subtotal + shipping,
        'cart_count': total_count,
    })


# ─────────────────────────────────────────────
#  Checkout & Order
# ─────────────────────────────────────────────

def checkout(request):
    """Checkout page with address form."""
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    items, subtotal = _cart_totals(cart)
    shipping = 0 if subtotal >= 500 else 40
    total = subtotal + shipping

    # Pre-fill from logged-in user
    initial = {}
    if request.user.is_authenticated:
        initial = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }

    context = {
        'cart_items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'initial': initial,
    }
    return render(request, 'orders/checkout.html', context)


def place_order(request):
    """Process checkout form and create Order."""
    if request.method != 'POST':
        return redirect('checkout')

    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    items, subtotal = _cart_totals(cart)
    shipping = 0 if subtotal >= 500 else 40
    total = subtotal + shipping

    # Create Order
    order = Order.objects.create(
        user         = request.user if request.user.is_authenticated else None,
        full_name    = request.POST.get('full_name'),
        email        = request.POST.get('email'),
        phone        = request.POST.get('phone'),
        address      = request.POST.get('address'),
        city         = request.POST.get('city'),
        state        = request.POST.get('state'),
        pincode      = request.POST.get('pincode'),
        total_amount = total,
        payment_method = request.POST.get('payment_method', 'Cash on Delivery'),
    )

    # Create OrderItems & reduce stock
    for item in items:
        product = item['product']
        qty     = item['quantity']
        OrderItem.objects.create(
            order        = order,
            product      = product,
            product_name = product.name,
            product_image = product.image_url,
            price        = product.price,
            quantity     = qty,
        )
        # Reduce stock
        product.stock = max(0, product.stock - qty)
        product.save(update_fields=['stock'])

    # Clear cart
    _save_cart(request, {})

    return redirect('order_confirmation', order_id=order.id)


def order_confirmation(request, order_id):
    """Thank-you / confirmation page."""
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/confirmation.html', {'order': order})


def my_orders(request):
    """Customer's own order history (requires login)."""
    if not request.user.is_authenticated:
        return redirect('user_login')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})
