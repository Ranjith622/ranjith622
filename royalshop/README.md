#  RoyalShop — Mini E-Commerce Django App

A full-featured, beautifully designed e-commerce web application built with:

- **Backend:** Python (Django 4.2)
- **Database:** MySQL
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Theme:** Royal Dark — Deep Green + Gold + White

---

##  Project Structure

```
royalshop/
├── manage.py
├── requirements.txt
├── royalshop/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/            # Products, Categories, Banners app
│   ├── models.py
│   ├── views.py          # Customer views
│   ├── admin_views.py    # Admin panel views
│   ├── admin_urls.py
│   ├── context_processors.py
│   └── management/commands/seed_data.py
├── orders/              # Cart (session) + Orders app
│   ├── models.py
│   └── views.py
├── users/               # Auth app
│   └── views.py
├── templates/
│   ├── base.html
│   ├── products/        # Home, list, detail
│   ├── orders/          # Cart, checkout, confirmation
│   ├── users/           # Login, register, profile
│   ├── admin_panel/     # Dashboard, products, orders, etc.
│   └── partials/        # Reusable product card
└── static/
    ├── css/royal.css     # Royal design system
    ├── css/admin.css     # Admin panel styles
    └── js/royal.js       # AJAX cart, interactions
```

---

##  Setup Instructions

### 1. Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

### 2. Create & Activate Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create MySQL Database
Open MySQL and run:
```sql
CREATE DATABASE royalshop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure Database Credentials
Open `royalshop/settings.py` and update:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'royalshop_db',
        'USER': 'root',           # ← your MySQL username
        'PASSWORD': 'yourpass',   # ← your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Seed Sample Data (optional but recommended!)
```bash
python manage.py seed_data
```
This creates:
-  Admin user: `admin` / `admin123`
-  6 Categories (Electronics, Clothing, Food, etc.)
-  16 Sample Products
-  3 Homepage Banners

### 8. Start the Development Server
```bash
python manage.py runserver
```

---

## 🌐 URLs

| Page | URL |
|------|-----|
|  Home | http://127.0.0.1:8000/ |
|  All Products | http://127.0.0.1:8000/products/ |
|  Cart | http://127.0.0.1:8000/orders/cart/ |
|  Checkout | http://127.0.0.1:8000/orders/checkout/ |
|  Register | http://127.0.0.1:8000/users/register/ |
|  Login | http://127.0.0.1:8000/users/login/ |
|  My Orders | http://127.0.0.1:8000/orders/my-orders/ |
|  **Admin Panel** | http://127.0.0.1:8000/admin-panel/ |
|  Django Admin | http://127.0.0.1:8000/django-admin/ |

---

##  Features

### Customer Features
-  **Hero Banner Carousel** — auto-sliding with offers and promotions
-  **Category filtering** with sidebar and pill navigation
-  **Search** by product name / description
-  **Sort** by price (asc/desc), name, or newest
-  **Price range filter**
-  **Pagination** (12 products per page)
-  **AJAX Cart** — add/update/remove without page reload
-  **Checkout** with shipping details form
-  **Order Confirmation** page
-  **Login, Register, Profile, My Orders**
-  **Fully Responsive** (mobile/tablet/desktop)

### Admin Features
-  **Secure admin login** (staff/superuser only)
-  **Dashboard** with stats and low-stock alerts
-  **Product CRUD** — add, edit, delete products
-  **Category Management** with Bootstrap icon support
-  **Banner Management** — control homepage carousel
-  **Order Management** — view all orders, update status
-  **Product search** in admin

---

## 🎨 Design System

| Token | Value |
|-------|-------|
| Primary | `#0B3D2E` (Deep Royal Green) |
| Gold | `#C9A227` |
| Background | `#0e0e0e` |
| Card BG | `#161616` |
| Font (headings) | Playfair Display |
| Font (body) | Jost |

---

##  Customisation Tips

- **Change theme colour** → edit CSS variables in `static/css/royal.css` `:root`
- **Add products via admin** → go to `/admin-panel/products/add/`
- **Change products per page** → edit `Paginator(products, 12)` in `products/views.py`
- **Free shipping threshold** → search `500` in `orders/views.py`
- **Add payment gateway** → extend the checkout view in `orders/views.py`

---

##  Notes

- Product images are stored in `media/products/`
- Banner images are stored in `media/banners/`
- Cart is session-based (no login required to shop)
- Orders are linked to the user if logged in, otherwise guest
- The Django built-in admin is also available at `/django-admin/`
