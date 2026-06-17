"""
Orders App - Models
====================
Cart (session-based) + Order + OrderItem database models.
"""
from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    """A placed order with customer details and items"""

    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('confirmed',  'Confirmed'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]

    # Customer info (guest checkout supported)
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name     = models.CharField(max_length=150)
    email         = models.EmailField()
    phone         = models.CharField(max_length=20)
    address       = models.TextField()
    city          = models.CharField(max_length=100)
    state         = models.CharField(max_length=100)
    pincode       = models.CharField(max_length=10)

    # Order info
    total_amount  = models.DecimalField(max_digits=12, decimal_places=2)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')

    # Timestamps
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} – {self.full_name}'

    @property
    def status_badge_class(self):
        return {
            'pending':    'warning',
            'confirmed':  'info',
            'processing': 'primary',
            'shipped':    'royal',
            'delivered':  'success',
            'cancelled':  'danger',
        }.get(self.status, 'secondary')


class OrderItem(models.Model):
    """A single line-item inside an order"""
    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product       = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name  = models.CharField(max_length=200)   # snapshot at order time
    product_image = models.CharField(max_length=500, blank=True)
    price         = models.DecimalField(max_digits=10, decimal_places=2)
    quantity      = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product_name} × {self.quantity}'
