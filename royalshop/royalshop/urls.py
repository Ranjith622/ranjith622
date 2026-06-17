"""
RoyalShop - Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),           # Django's built-in admin
    path('', include('products.urls')),               # Products & home
    path('orders/', include('orders.urls')),          # Cart, checkout, orders
    path('users/', include('users.urls')),            # Login, register, profile
    path('admin-panel/', include('products.admin_urls')),  # Custom admin panel
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
