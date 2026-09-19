import os
from pathlib import Path

# Build paths inside the project /home/dave/Documents/tmp/mp_test/src/django/
BASE_DIR = Path(__file__).resolve().parent.parent

# Security - Replace with a random string in production
# SECRET_KEY = 'django-insecure-change-me-in-production-12345'
SECRET_KEY = 'RFSwarm-Django-8139'

# SECURITY WARNING: keep() is used for development. In production, set DEBUG to False.
DEBUG = True

# ALLOWED_HOSTS defines which domains can drag content from this server
ALLOWED_HOSTS = ['*']

# List of installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'RFSwarmDjango.api_v1', # Your custom app
]

# Middleware used in the request/response processing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

# WSGI configuration
WSGI_APPLICATION = 'RFSwarmDjango.django_project.wsgi.application'

# Database configuration (using SQLite for local development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'NAME': ':memory:',
    }
}

# URL configuration
ROOT_URLCONF = 'RFSwarmDjango.django_project.urls'

# Default auto field (required in newer Django versions)
DEFAULT_AUTO_FIELD = 'django.db.models.Model.AutoField'

# Internationalisation
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True

# Static files configuration
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Placeholders for the queues injected by django_worker.py
Q_API_RESQUEST = None
Q_API_RESULT = None
SHARED_STATE = None