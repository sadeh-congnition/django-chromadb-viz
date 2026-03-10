"""
Test settings for Django ChromaDB Viz tests.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "test-secret-key-for-testing-only"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_chromadb_viz",
]

MIDDLEWARE = []

ROOT_URLCONF = "django_chromadb_viz.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_chromadb_viz.wsgi.application"

# Database
# Use in-memory SQLite for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ChromaDB test settings
CHROMADB_PATH = BASE_DIR / "test_chromadb"
CHROMADB_HOST = "localhost"
CHROMADB_PORT = 8000

# UI Settings
CHROMADB_VIZ_ITEMS_PER_PAGE = 20
CHROMADB_VIZ_MAX_CONTENT_LENGTH = 1000

# Security settings
CHROMADB_VIZ_ALLOW_DELETION = True
CHROMADB_VIZ_ALLOW_MODIFICATION = True

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django_chromadb_viz": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
