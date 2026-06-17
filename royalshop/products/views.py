"""
Products App - Views
=====================
Handles home page, product listing, product detail, and search.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Product, Category, Banner


def home(request):
    """Homepage: banner slider + featured products"""
    banners = Banner.objects.filter(is_active=True).order_by('order')
    featured_products = Product.objects.filter(is_featured=True, is_active=True, stock__gt=0)[:8]
    latest_products = Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:8]
    categories = Category.objects.all()

    context = {
        'banners': banners,
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)


def product_list(request):
    """
    All products page with:
    - Search by name/description
    - Filter by category
    - Filter by price range
    - Pagination (12 per page)
    """
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # --- Search ---
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # --- Category Filter ---
    category_slug = request.GET.get('category', '')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    # --- Price Filter ---
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # --- Sort ---
    sort = request.GET.get('sort', '-created_at')
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'newest': '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    # --- Pagination ---
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'active_category': active_category,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'total_count': products.count(),
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Single product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    context = {
        'product': product,
        'related_products': related,
    }
    return render(request, 'products/product_detail.html', context)
