"""
Context Processors
===================
Injects cart count and categories into every template context.
"""
from .models import Category


def cart_count(request):
    """Returns number of items in the cart (from session)"""
    cart = request.session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return {'cart_count': count}


def categories_list(request):
    """Returns all categories for the navbar"""
    categories = Category.objects.all()
    return {'all_categories': categories}
