import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-me')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party packages
    'rest_framework',
    'corsheaders',
    'django_extensions',
    
    # Local Apps
    'invoices.apps.InvoicesConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'invoice_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'invoice_system.wsgi.application'

# Database Configuration (Render DATABASE_URL / Local PostgreSQL with automatic SQLite fallback)
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = os.getenv('USE_POSTGRES', 'False').lower() in ('true', '1', 't')

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif USE_POSTGRES:
    # Verify if PostgreSQL port is open/accepting connections
    import socket
    postgres_host = os.getenv('DB_HOST', 'localhost')
    postgres_port = int(os.getenv('DB_PORT', '5432'))
    
    postgres_active = False
    try:
        with socket.create_connection((postgres_host, postgres_port), timeout=1.0):
            postgres_active = True
    except Exception:
        postgres_active = False

    if postgres_active:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', 'invoice_db'),
                'USER': os.getenv('DB_USER', 'postgres'),
                'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
                'HOST': postgres_host,
                'PORT': str(postgres_port),
            }
        }
    else:
        print("\n" + "="*85)
        print("WARNING: Local PostgreSQL service is NOT running on port 5432.")
        print("Automatically falling back to embedded SQLite database (db.sqlite3) for stability.")
        print("To switch back to PostgreSQL, run: sudo service postgresql start")
        print("="*85 + "\n")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }




# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# AWS S3 Storage Settings (COMMENTED OUT - AWS plan expired)
# ==============================================================================
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# if AWS_STORAGE_BUCKET_NAME:
#     AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
#     AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
#     AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
#     
#     STORAGES = {
#         "default": {
#             "BACKEND": "storages.backends.s3.S3Storage",
#             "OPTIONS": {
#                 "location": "media",
#             },
#         },
#         "staticfiles": {
#             "BACKEND": "storages.backends.s3.S3Storage",
#             "OPTIONS": {
#                 "location": "static",
#             },
#         },
#     }
#     # Static & Media URL overrides for S3
#     STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
#     MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
# else:
#     # Static files (CSS, JavaScript, Images)
#     STATIC_URL = '/static/'
#     # Media files (Uploaded Invoices)
#     MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# Media files (Uploaded Invoices)
MEDIA_URL = '/media/'

# WhiteNoise storage for static files & local FileSystemStorage for media files
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True

# Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
