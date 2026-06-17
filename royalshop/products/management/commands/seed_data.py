"""
Management Command: seed_data
==============================
Run with:  python manage.py seed_data

Creates:
  - Admin superuser (admin / admin123)
  - Sample categories
  - Sample products
  - Sample banners
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product, Banner
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with sample categories, products, and banners'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('\n🌱 Seeding RoyalShop database...\n'))

        # ── Admin user ──────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@royalshop.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('  ✓ Superuser created  →  admin / admin123'))
        else:
            self.stdout.write('  – Superuser already exists, skipping.')

        # ── Categories ──────────────────────────────────────────────
        categories_data = [
            {'name': 'Electronics',  'icon': 'bi-laptop',        'description': 'Gadgets & devices'},
            {'name': 'Clothing',     'icon': 'bi-bag-heart',     'description': 'Fashion & apparel'},
            {'name': 'Food & Grocery','icon': 'bi-cart3',        'description': 'Fresh & packaged food'},
            {'name': 'Home & Living','icon': 'bi-house-heart',   'description': 'Décor & furniture'},
            {'name': 'Books',        'icon': 'bi-book',          'description': 'Fiction & non-fiction'},
            {'name': 'Beauty',       'icon': 'bi-stars',         'description': 'Skincare & cosmetics'},
        ]
        cats = {}
        for data in categories_data:
            cat, created = Category.objects.get_or_create(name=data['name'], defaults=data)
            cats[data['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Category: {data['name']}"))

        # ── Products ────────────────────────────────────────────────
        products_data = [
            # Electronics
            {'name': 'Royal Wireless Earbuds', 'category': 'Electronics', 'price': '1299', 'original_price': '1999', 'stock': 50, 'is_featured': True,
             'description': 'Premium sound quality with active noise cancellation. 30-hour battery life.'},
            {'name': 'Smart HD Webcam 4K', 'category': 'Electronics', 'price': '2499', 'original_price': '3499', 'stock': 30, 'is_featured': True,
             'description': 'Crystal-clear 4K video for meetings and streaming. Plug-and-play USB-C.'},
            {'name': 'Mechanical Keyboard', 'category': 'Electronics', 'price': '3199', 'stock': 25,
             'description': 'RGB backlit, tactile switches. 100% anti-ghosting. Compact TKL layout.'},
            {'name': 'USB-C Fast Charger 65W', 'category': 'Electronics', 'price': '899', 'original_price': '1299', 'stock': 80,
             'description': '65W GaN charger. Charges laptop, phone, and tablet simultaneously.'},

            # Clothing
            {'name': 'Royal Silk Kurta', 'category': 'Clothing', 'price': '1599', 'original_price': '2200', 'stock': 40, 'is_featured': True,
             'description': 'Luxurious silk fabric, hand-embroidered borders. Available in S/M/L/XL.'},
            {'name': 'Embroidered Saree', 'category': 'Clothing', 'price': '3499', 'original_price': '5000', 'stock': 15,
             'description': 'Pure cotton saree with zari embroidery border. 6-yard drape, unstitched blouse.'},
            {'name': 'Men\'s Linen Shirt', 'category': 'Clothing', 'price': '799', 'stock': 60,
             'description': 'Breathable linen, perfect for summer. Slim-fit design.'},

            # Food & Grocery
            {'name': 'Royal Basmati Rice 5kg', 'category': 'Food & Grocery', 'price': '449', 'original_price': '550', 'stock': 100,
             'description': 'Premium long-grain aged basmati. Extra fragrant. Non-GMO.'},
            {'name': 'Organic Honey 500g', 'category': 'Food & Grocery', 'price': '349', 'stock': 75, 'is_featured': True,
             'description': 'Raw, unfiltered wildflower honey. Sourced from Himalayan apiaries.'},
            {'name': 'Cold-Pressed Coconut Oil', 'category': 'Food & Grocery', 'price': '299', 'stock': 90,
             'description': 'Virgin cold-pressed. No preservatives. Multi-use: cooking & skincare.'},

            # Home & Living
            {'name': 'Brass Diya Set (6 pcs)', 'category': 'Home & Living', 'price': '699', 'original_price': '950', 'stock': 35, 'is_featured': True,
             'description': 'Handcrafted pure brass oil lamps. Ideal for pooja & décor.'},
            {'name': 'Handwoven Jute Basket', 'category': 'Home & Living', 'price': '549', 'stock': 45,
             'description': 'Eco-friendly storage basket. 12" diameter. Perfect for plants or laundry.'},

            # Books
            {'name': 'The Arthashastra — Kautilya', 'category': 'Books', 'price': '399', 'stock': 55,
             'description': 'Ancient Indian treatise on statecraft. New translation with commentary.'},
            {'name': 'Atomic Habits', 'category': 'Books', 'price': '349', 'original_price': '499', 'stock': 70, 'is_featured': True,
             'description': 'James Clear\'s #1 NY Times bestseller. Build good habits, break bad ones.'},

            # Beauty
            {'name': 'Kumkumadi Face Serum', 'category': 'Beauty', 'price': '849', 'original_price': '1200', 'stock': 40, 'is_featured': True,
             'description': 'Ayurvedic brightening serum with saffron extract. 30ml.'},
            {'name': 'Rose Water Toner 200ml', 'category': 'Beauty', 'price': '299', 'stock': 85,
             'description': 'Pure Bulgarian rose water. Alcohol-free. Suits all skin types.'},
        ]

        for pdata in products_data:
            cat_name = pdata.pop('category')
            cat = cats.get(cat_name)
            name = pdata['name']
            if not Product.objects.filter(name=name).exists():
                Product.objects.create(category=cat, **pdata)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Product: {name}"))

        # ── Banners ─────────────────────────────────────────────────
        banners_data = [
            {
                'title': 'Grand Festive Sale',
                'subtitle': 'Up to 50% off on Premium Products. Limited time only.',
                'badge_text': '🎉 UP TO 50% OFF',
                'button_text': 'Shop Now',
                'button_url': '/products/',
                'bg_color': '#0B3D2E',
                'order': 1,
            },
            {
                'title': 'New Electronics Arrivals',
                'subtitle': 'Discover the latest gadgets handpicked for tech royalty.',
                'badge_text': '⚡ NEW ARRIVALS',
                'button_text': 'Explore',
                'button_url': '/products/?category=electronics',
                'bg_color': '#12294a',
                'order': 2,
            },
            {
                'title': 'Royal Fashion Collection',
                'subtitle': 'Dress like royalty. Premium fabrics, timeless designs.',
                'badge_text': '👑 EXCLUSIVE',
                'button_text': 'View Collection',
                'button_url': '/products/?category=clothing',
                'bg_color': '#2e0b3d',
                'order': 3,
            },
        ]
        for bdata in banners_data:
            if not Banner.objects.filter(title=bdata['title']).exists():
                Banner.objects.create(**bdata)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Banner: {bdata['title']}"))

        self.stdout.write(self.style.SUCCESS('\n🎉 Seeding complete!\n'))
        self.stdout.write(self.style.WARNING('  Admin credentials → username: admin  |  password: admin123'))
        self.stdout.write(self.style.WARNING('  Admin panel URL  → http://127.0.0.1:8000/admin-panel/\n'))
