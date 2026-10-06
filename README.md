# PharmaCare - Modern Pharmacy Store & Express Medicine Delivery System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-red.svg)](https://www.django-rest-framework.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI_3-drf--spectacular-teal.svg)](https://drf-spectacular.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

PharmaCare is an enterprise-grade digital pharmacy storefront and express medicine delivery platform engineered in Python and Django. It integrates prescription uploads, clinical pharmacist verifications, inventory lot & batch tracking, immutable audit trails, and multi-role operations across Customers, Pharmacists, Inventory Managers, Delivery Couriers, and Administrators.

---

## 🚀 Key Features by Role

### 🩺 Customer Portal
- **Browse & Search:** Search medicines by commercial brand, generic active ingredient, or therapeutic category.
- **Detailed Clinical Specs:** View dosage form, strength, storage guidelines, batch expiration dates, and user reviews.
- **Prescription Upload:** Securely upload prescription files (PDF, JPG, PNG up to 5MB) during checkout or in advance.
- **Real-Time Cart & Checkout:** Five-step checkout with instant tax calculations, free delivery over $50, and COD/Card options.
- **Order Tracking:** Live status timeline from prescription verification to courier dispatch.
- **Wishlist & Invoices:** Save items for refills and print official tax invoices.

### 🛡️ Pharmacist Verification Hub
- **Clinical Review Desk:** Dedicated interface to inspect patient prescription documents.
- **Approve or Reject:** Approve prescriptions or reject with mandatory clinical reason notes.
- **Regulated Order Gatekeeping:** Orders containing prescription-only (Rx) medications cannot be fulfilled until approved.
- **Batch Expiry Monitoring:** Real-time visibility into medication lots expiring within 60 days.

### 📦 Inventory & Batch Manager
- **Lot Tracking:** Record incoming batches with manufacturing date, expiration date, supplier, and unit cost.
- **Audit Ledger:** Every manual stock adjustment records a permanent `StockTransaction` audit entry.
- **Low Stock & Expiry Alerts:** Filter products by low stock threshold or quarantine expired batches.

### 🚚 Delivery Courier Hub
- **Job Claiming:** Couriers accept unassigned deliveries.
- **Status Lifecycle:** Transition shipments through Assigned &rarr; Picked Up &rarr; Out for Delivery &rarr; Delivered.
- **COD Reconciliation:** Prompts driver to collect exact cash amount before handing over packages.

### ⚙️ Executive Administrator
- **Operational Metrics:** Daily & monthly sales, order distribution, and customer metrics.
- **System Audit Log:** Permanent audit records of every critical action with user and IP timestamps.
- **Full Django Admin:** Complete model introspection via `/admin/`.

---

## 🔐 Demo Credentials

PharmaCare comes pre-seeded with 5 role-based accounts:

| Role | Username | Password | Operational Access |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Full System Administration (`/dashboard/admin/`, `/admin/`) |
| **Pharmacist** | `pharmacist` | `pharma123` | Prescription Review & Clinical Desk (`/dashboard/pharmacist/`) |
| **Inventory Manager** | `inventory` | `inven123` | Stock & Batch Adjustments (`/inventory/`) |
| **Delivery Courier** | `delivery` | `deliver123` | Driver Dispatch & Delivery Tracking (`/deliveries/`) |
| **Customer** | `customer` | `customer123` | Storefront, Cart, Prescriptions, Orders (`/dashboard/customer/`) |

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11+, Django 5.1, Django REST Framework 3.15
- **Authentication:** Django Auth + SimpleJWT (Bearer Tokens)
- **Database:** SQLite (default development) / PostgreSQL (production-ready)
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, Vanilla JavaScript (ES6+ AJAX)
- **API Documentation:** OpenAPI 3 schema via `drf-spectacular` & Swagger UI
- **Styling:** Custom Healthcare Palette CSS (`--primary-color: #0d9488`)

---

## 📖 REST API Documentation

PharmaCare provides a complete REST API with JWT authentication:

- **Interactive Swagger UI:** [`/api/docs/`](http://localhost:8000/api/docs/)
- **ReDoc Documentation:** [`/api/redoc/`](http://localhost:8000/api/redoc/)
- **OpenAPI Schema (JSON/YAML):** [`/api/schema/`](http://localhost:8000/api/schema/)

### Core API Endpoints

```
POST /api/v1/auth/token/           # Obtain JWT access and refresh tokens
POST /api/v1/auth/token/refresh/   # Refresh JWT token
GET  /api/v1/auth/me/              # Current authenticated user details
GET  /api/v1/products/             # List active medicines with filters & search
GET  /api/v1/categories/           # List pharmacy categories
GET  /api/v1/cart/                 # Retrieve current cart
POST /api/v1/cart/add/             # Add item to cart
POST /api/v1/cart/remove/          # Remove item from cart
GET  /api/v1/orders/               # User orders list
POST /api/v1/orders/               # Submit new order checkout
GET  /api/v1/prescriptions/        # User prescriptions list
POST /api/v1/prescriptions/        # Upload new prescription
POST /api/v1/prescriptions/{id}/verify/ # Pharmacist approve/reject
GET  /api/v1/deliveries/           # Courier deliveries list
POST /api/v1/deliveries/{track}/update-status/ # Update delivery status
```

---

## 💻 Quick Start & Installation

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/example/pharmacare.git
cd pharmacare
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply Migrations & Seed Data

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_pharmacy_data
```

### 4. Run Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Visit [http://localhost:8000](http://localhost:8000) in your browser!

---

## 🧪 Running Automated Tests

Run the test suite covering products, cart, checkout, prescriptions, and REST API:

```bash
python manage.py test tests/
```

---

## 🏛️ Architecture & App Structure

```
pharmacare/
├── api/                  # REST API viewsets, serializers, and OpenAPI schemas
├── apps/
│   ├── accounts/         # Custom User, Profile, Address models and auth views
│   ├── cart/             # Session/DB shopping cart with real-time tax & stock checks
│   ├── common/           # AuditLog, TimeStampedModel, utility functions
│   ├── dashboard/        # Role-based management dashboards (Admin, Pharmacist, Customer)
│   ├── deliveries/       # Courier assignments, tracking numbers, and handover notes
│   ├── inventory/        # Batch tracking, expiry monitoring, and stock transactions
│   ├── notifications/    # In-app customer and staff notification alerts
│   ├── orders/           # Checkout pipeline, order items, and PDF/HTML invoices
│   ├── payments/         # Payment transactions, COD and online mock gateways
│   ├── prescriptions/    # Document upload, clinical review & pharmacist verification
│   ├── products/         # Catalog, Category, Product, and Wishlist models
│   └── reviews/          # Verified customer ratings and feedback
├── config/               # Django settings (base, dev, prod), WSGI, ASGI, and root URLs
├── static/               # CSS, JavaScript (AJAX cart, notifications, checkout), icons
├── templates/            # Django HTML templates (Bootstrap 5.3)
└── tests/                # Automated test suites
```

---

## 📜 License

This project is licensed under the MIT License.
