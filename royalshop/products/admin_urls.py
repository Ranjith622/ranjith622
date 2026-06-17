"""Custom Admin Panel URLs"""
from django.urls import path
from . import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('login/', admin_views.admin_login, name='admin_login'),
    path('logout/', admin_views.admin_logout, name='admin_logout'),
    # Product management
    path('products/', admin_views.admin_products, name='admin_products'),
    path('products/add/', admin_views.admin_product_add, name='admin_product_add'),
    path('products/edit/<int:pk>/', admin_views.admin_product_edit, name='admin_product_edit'),
    path('products/delete/<int:pk>/', admin_views.admin_product_delete, name='admin_product_delete'),
    # Category management
    path('categories/', admin_views.admin_categories, name='admin_categories'),
    path('categories/add/', admin_views.admin_category_add, name='admin_category_add'),
    path('categories/delete/<int:pk>/', admin_views.admin_category_delete, name='admin_category_delete'),
    # Order management
    path('orders/', admin_views.admin_orders, name='admin_orders'),
    path('orders/<int:pk>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('orders/<int:pk>/update-status/', admin_views.admin_order_update_status, name='admin_order_update_status'),
    # Banner management
    path('banners/', admin_views.admin_banners, name='admin_banners'),
    path('banners/add/', admin_views.admin_banner_add, name='admin_banner_add'),
    path('banners/delete/<int:pk>/', admin_views.admin_banner_delete, name='admin_banner_delete'),
]
