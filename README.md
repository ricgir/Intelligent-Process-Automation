# Intelligent Process Automation — Django Invoice Processing System

An enterprise-grade **Django + Django REST Framework (DRF)** application that automates invoice text extraction (OCR via `pytesseract` and `pdfplumber`), structures data using **Google Gemini 1.5 Pro AI**, and stores relational header and line-item records in a **Local PostgreSQL** database.

---

## Architecture Overview

```
Intelligent-Process-Automation/
├── .env                       # Environment variables (DB credentials, Gemini API key)
├── .gitignore                 # Excludes secrets, cache, and media files
├── manage.py                  # Django CLI entry point
├── requirements.txt           # Django, DRF, PostgreSQL & AI dependencies
├── check_db.py                # Database connection utility script
├── invoice_system/            # Django project settings & root URLs
│   ├── settings.py
│   └── urls.py
├── invoices/                  # Django app module
│   ├── models.py              # Invoice & InvoiceLineItem ORM models
│   ├── admin.py               # Admin interface registration
│   ├── serializers.py         # DRF serializers (Header + Line Items)
│   ├── views.py               # DRF ViewSet & HTML template views
│   ├── services/              # Business logic isolation
│   │   ├── ocr_service.py     # Pytesseract & pdfplumber OCR
│   │   ├── gemini_service.py  # Gemini 1.5 Pro AI integration
│   │   └── invoice_processor.py # Database persistence orchestrator
│   └── tests.py               # Automated unit & API tests
└── templates/                 # Responsive HTML UI templates
    ├── index.html
    └── results.html
```

---

## Setup & Installation

### 1. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Secrets Configuration (`.env`)
Create or edit `.env` in the project root:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Local PostgreSQL Database Credentials
DB_NAME=invoice_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Gemini AI API Key
GEMINI_API_KEY=[GCP_API_KEY]
```

---

## Database Migrations & Superuser

### 1. Apply Database Migrations
Ensure PostgreSQL service is running locally, then execute:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Admin Superuser
```bash
python manage.py createsuperuser
```

---

## Running the Application

Start the Django development server:
```bash
python manage.py runserver
```

- **Web Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **REST API Endpoints**: [http://127.0.0.1:8000/api/invoices/](http://127.0.0.1:8000/api/invoices/)
- **Django Admin GUI**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## REST API Usage

### Upload & Process Invoice Document
```bash
curl -X POST http://127.0.0.1:8000/api/invoices/upload/ \
  -F "file=@sample_invoice.pdf"
```

### List All Stored Invoices
```bash
curl -H "Accept: application/json" http://127.0.0.1:8000/api/invoices/
```

---

## Running Tests

Execute the automated test suite:
```bash
python manage.py test invoices
```
