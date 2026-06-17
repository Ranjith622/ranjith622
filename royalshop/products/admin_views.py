"""
Admin Panel Views
==================
Custom admin dashboard for managing products, orders, categories, banners.
Requires staff/superuser access.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from .models import Product, Category, Banner
from orders.models import Order


def is_admin(user):
    """Check if user is staff or superuser"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_login(request):
    """Admin login page"""
    if is_admin(request.user):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')

    return render(request, 'admin_panel/login.html')


def admin_logout(request):
    """Admin logout"""
    logout(request)
    return redirect('admin_login')


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_dashboard(request):
    """Admin dashboard with summary stats"""
    stats = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue': Order.objects.filter(status__in=['delivered', 'shipped']).aggregate(
            total=Sum('total_amount'))['total'] or 0,
        'total_categories': Category.objects.count(),
        'low_stock': Product.objects.filter(stock__lte=5, is_active=True).count(),
    }
    recent_orders = Order.objects.order_by('-created_at')[:10]
    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True)[:5]

    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_products(request):
    """List all products"""
    products = Product.objects.all().select_related('category').order_by('-created_at')
    # Search
    q = request.GET.get('q', '')
    if q:
        products = products.filter(name__icontains=q)
    context = {'products': products, 'q': q}
    return render(request, 'admin_panel/products.html', context)


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_product_add(request):
    """Add a new product"""
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        original_price = request.POST.get('original_price') or None
        stock = request.POST.get('stock', 0)
        is_featured = request.POST.get('is_featured') == 'on'
        image = request.FILES.get('image')

        try:
            product = Product.objects.create(
                name=name,
                category_id=category_id if category_id else None,
                description=description,
                price=price,
                original_price=original_price,
                stock=stock,
                is_featured=is_featured,
                image=image,
            )
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('admin_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {e}')

    return render(request, 'admin_panel/product_form.html', {'categories': categories, 'action': 'Add'})


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_product_edit(request, pk):
    """Edit an existing product"""
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('name')
        cat_id = request.POST.get('category')
        product.category_id = cat_id if cat_id else None
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price')
        orig = request.POST.get('original_price')
        product.original_price = orig if orig else None
        product.stock = request.POST.get('stock', 0)
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_active = request.POST.get('is_active') == 'on'
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.slug = ''  # Reset slug to regenerate
        product.save()
        messages.success(request, f'Product "{product.name}" updated!')
        return redirect('admin_products')

    return render(request, 'admin_panel/product_form.html', {
        'categories': categories, 'product': product, 'action': 'Edit'
    })


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_product_delete(request, pk):
    """Delete a product"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
    return redirect('admin_products')


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_categories(request):
    """List and manage categories"""
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    return render(request, 'admin_panel/categories.html', {'categories': categories})


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_category_add(request):
    """Add a category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', 'bi-grid')
        try:
            cat = Category.objects.create(name=name, description=description, icon=icon)
            messages.success(request, f'Category "{cat.name}" added!')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('admin_categories')


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_category_delete(request, pk):
    """Delete a category"""
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Category "{name}" deleted.')
    return redirect('admin_categories')


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_orders(request):
    """List all orders with filter by status"""
    orders = Order.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    context = {'orders': orders, 'status_filter': status_filter, 'status_choices': Order.STATUS_CHOICES}
    return render(request, 'admin_panel/orders.html', context)


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_order_detail(request, pk):
    """View order details"""
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'admin_panel/order_detail.html', {
        'order': order, 'status_choices': Order.STATUS_CHOICES
    })


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_order_update_status(request, pk):
    """Update order status via POST"""
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('admin_order_detail', pk=pk)


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_banners(request):
    """List all banners"""
    banners = Banner.objects.all().order_by('order')
    return render(request, 'admin_panel/banners.html', {'banners': banners})


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_banner_add(request):
    """Add a banner"""
    if request.method == 'POST':
        try:
            Banner.objects.create(
                title=request.POST.get('title'),
                subtitle=request.POST.get('subtitle', ''),
                badge_text=request.POST.get('badge_text', ''),
                button_text=request.POST.get('button_text', 'Shop Now'),
                button_url=request.POST.get('button_url', '/'),
                bg_color=request.POST.get('bg_color', '#0B3D2E'),
                order=request.POST.get('order', 0),
                image=request.FILES.get('image'),
            )
            messages.success(request, 'Banner added successfully!')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('admin_banners')


@user_passes_test(is_admin, login_url='/admin-panel/login/')
def admin_banner_delete(request, pk):
    """Delete a banner"""
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Banner deleted.')
    return redirect('admin_banners')
