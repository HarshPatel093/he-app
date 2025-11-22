"""
Django settings for the Holiday Explorers Scheduling & Feedback System.

This configuration file defines the core application setup including:
- Installed apps
- Middleware 
- Template rendering configuration
- Database connection
- Static and media file handling
- Authentication settings
- Email backend configuration
- Automatic superuser creation

Environment variables are loaded using python-decouple for security purpose.
"""

from pathlib import Path
from decouple import config
import os
from dotenv import load_dotenv

# Load environmental variables from .env file (used for secret keys and database credentials)
load_dotenv()

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key is stored in environment variable for security purpose
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Allow all hosts
ALLOWED_HOSTS = ['*']

# Applications installed in this project
INSTALLED_APPS = [
    'users.apps.UsersConfig',   
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
]

# MIDDLEWARE
# Processes every request in this order
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL Configuration
ROOT_URLCONF = 'core.urls'

# Template Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application for deployment
WSGI_APPLICATION = 'core.wsgi.application'

# DATABASE Configuration
# PostgreSQL details loaded from .env file for security
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Login/Logout Redirects
LOGIN_REDIRECT_URL = 'dashboard_redirect'
LOGOUT_REDIRECT_URL='login'

# Timezone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Adelaide'
USE_I18N = True
USE_TZ = True

# Static and Media File Handling
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auto superuser creation (Development Only)
# Prevents Django auto-reload from creating user twice
if os.environ.get('RUN_MAIN') == 'true':  # prevents running twice with autoreload
    try:
        from create_superuser_if_not_exists import run as create_superuser
        create_superuser()
    except Exception as e:
        print(f"Error creating superuser: {e}")

# Email backend Configuration
# Used for password reset
EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")