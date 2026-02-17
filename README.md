# 🛍️ ShopX | Premium Multi-Category Marketplace

ShopX is a sophisticated multi-vendor e-commerce platform built with **Django 5.2**.  
It supports role-based access control, AJAX-powered interactions, real-time vendor analytics, and a modern glassmorphism UI.

Designed as a scalable commercial-ready architecture for multi-category marketplaces.

---

## 🚀 Key Features

### 👤 User & Role Management

- Role-Based Access Control (RBAC)
  - Admin
  - Vendor
  - Customer
- Automatic profile creation using Django Signals
- Profile management (address, phone, profile image)
- Secure authentication & authorization

---

### 🏪 Multi-Vendor System

- Vendor Dashboard with:
  - Total Revenue calculation
  - Sales count aggregation
  - Optimized database queries
- Vendor Inventory Management:
  - Add / Edit / Delete products
  - Secure ownership-based permissions
- Custom decorators for access control

---

### 🛒 Shopping Experience

- AJAX-powered cart (no page refresh)
- Real-time quantity updates
- Wishlist system with heart toggle (AJAX)
- Advanced search:
  - Keyword search
  - Category filtering
  - URL-based persistence

---

### 📦 Orders & Transactions

- Complete order tracking system
- Status flow:
  - Pending → Processing → Completed
- Automatic stock deduction after checkout
- Invoice generation with print-ready receipt view

---

## 🛠️ Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | Python 3.10+, Django 5.2 |
| Frontend | Bootstrap 5.3, Vanilla JS (Fetch API) |
| Database | SQLite (Development) |
| Production DB | PostgreSQL |
| Styling | Custom CSS3 (Glassmorphism + Backdrop Filters) |

---

## 📂 Project Structure

.
├── ecom_project/ # Core project configuration
├── users/ # Authentication, Profiles, RBAC
├── products/ # Catalog, Vendor, Wishlist logic
├── orders/ # Cart, Checkout, Order tracking
├── templates/ # HTML templates
├── static/ # CSS, JS, assets
└── media/ # Uploaded images


---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

git clone <repository-url>
cd ecom_project


---

### 2️⃣ Create & Activate Virtual Environment

**Using Conda:**

conda create -n pyfullstack python=3.10
conda activate pyfullstack


**Or using venv:**

python -m venv venv
source venv/bin/activate


---

### 3️⃣ Install Dependencies

pip install django pillow


---

### 4️⃣ Apply Migrations

python manage.py makemigrations
python manage.py migrate


---

### 5️⃣ Create Superuser

python manage.py createsuperuser


---

### 6️⃣ Run Development Server

python manage.py runserver


---

## 🔐 Roles Overview

| Role | Permissions |
|------|-------------|
| Admin | Full control via Django Admin |
| Vendor | Manage own products + view analytics |
| Customer | Browse, add to cart, order, wishlist |

---

## 📊 Vendor Dashboard Highlights

- Database aggregation using Django ORM
- Real-time revenue computation
- Optimized queries for performance
- Secure vendor-only data access

---

## 📌 Future Improvements (Production Ready Ideas)

- Stripe / Razorpay integration
- JWT Authentication
- Redis caching
- Celery for background tasks
- Docker support
- Deployment on AWS / Railway / Render

