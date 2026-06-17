"""
Products App - Models
======================
Defines Category and Product database models.
"""
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product category (e.g., Electronics, Clothing, Food)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-grid', help_text='Bootstrap icon class')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model with all details"""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Original price for showing discount')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text='Show on banner/homepage')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        """Calculate discount percentage if original price exists"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return '/static/images/no-image.png'

    def __str__(self):
        return self.name


class Banner(models.Model):
    """Homepage banner/carousel slides"""
    BANNER_TYPES = [
        ('offer', 'Special Offer'),
        ('product', 'Product Showcase'),
        ('discount', 'Discount Banner'),
        ('promo', 'Promotion'),
    ]
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    badge_text = models.CharField(max_length=50, blank=True, help_text='e.g., "UP TO 50% OFF"')
    button_text = models.CharField(max_length=50, default='Shop Now')
    button_url = models.CharField(max_length=200, default='/')
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    bg_color = models.CharField(max_length=7, default='#0B3D2E', help_text='Hex color for background')
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='offer')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
