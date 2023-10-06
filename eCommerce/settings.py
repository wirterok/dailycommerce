"""
Django settings for eCommerce project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import json
import os
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "%kb49tccw_66knu-=uw%flkju=e#e(4eqh4++uj(1!tc@if^iw"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["188.242.24.140", "68.183.123.191", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # local
    "db.core",
    "db.account",
    "db.orders.apps.OrdersConfig",
    "db.payment",
    "db.product",
    "db.service",
    "db.warehouse",
    "db.settings",
    "db.local_settings",
    # 3-party
    "mptt",
    "rest_framework",
    "django_extensions",
    "corsheaders",
    "drf_yasg",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # custom
    "eCommerce.middleware.DatabaseMiddleware",
]

ROOT_URLCONF = "eCommerce.urls"

TEMPLATE_DIRS = (os.path.join(BASE_DIR, "templates"),)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATE_DIRS,
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

WSGI_APPLICATION = "eCommerce.wsgi.application"

# if DEBUG:
DATABASE_HOST_SETTINGS = {
    "ENGINE": "django.db.backends.postgresql_psycopg2",
    "NAME": "pysonet",
    "USER": "postgres",
    "PASSWORD": "root",
    "HOST": "localhost",
    "PORT": "5432",
}
#     DB_CONFIG_FILE = "test_db_conf.json"

# else:
# DATABASE_HOST_SETTINGS = {
#     "ENGINE": "django.db.backends.postgresql_psycopg2",
#     "NAME": "ecommerce",
#     "USER": "ecm",
#     "PASSWORD": "PsGLQ34Hbv",
#     "HOST": "localhost",
#     "PORT": "5432",
# }
DB_CONFIG_FILE = "db_conf.json"


DEFAULT_DATABASES = {
    "default": {
        "OPTIONS": {"options": "-c search_path=general_schema"},
        "SCHEMA_NAME": "general_schema",
        **DATABASE_HOST_SETTINGS,
    },
    "core": {
        "OPTIONS": {"options": "-c search_path=core_schema"},
        "SCHEMA_NAME": "core_schema",
        **DATABASE_HOST_SETTINGS,
    },
}

DATABASES = dict(**DEFAULT_DATABASES, **json.load(open(os.path.join(BASE_DIR, DB_CONFIG_FILE))))

CORE_DB_NAME = "core"

DATABASE_ROUTERS = ["eCommerce.middleware.SubdomainRouter"]
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
# STATICFILES_DIRS = [STATIC_ROOT]

AUTH_USER_MODEL = "account.Customer"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "eCommerce.authentication.ExtendedTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
MAILER_EMAIL_BACKEND = EMAIL_BACKEND
EMAIL_HOST = "mx2fa3.netcup.net"
EMAIL_HOST_PASSWORD = "7refrain.unmixable.regretful.paced5.jaybird"
EMAIL_HOST_USER = "info@kamerabox.com"
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

HOST_URL = "http://127.0.0.1:8850/api/v1"

CORS_ALLOW_HEADERS = list(default_headers) + [
    "tenant-id",
]

CORS_ALLOWED_ORIGINS = [
    "http://68.183.123.191",
    "http://68.183.123.191:8000",
    "http://188.242.24.140",
    "http://188.242.24.140:8000",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]