"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from corsheaders.defaults import default_headers

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# Set File Upload Permissions
FILE_UPLOAD_PERMISSIONS = 0o644

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "w(kj_&g1ji(000^@2gi=fr8-vl4nqo1+by!lubz6!^n!=d0-#t"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ALLOW_HEADERS = default_headers + ('language-code',)
ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    "https://admin.nextpro.io",
    "https://auction.nextpro.io",
    "https://uat.e-auction.admin.nextpro.io",
    "https://uat.e-auction.user.nextpro.io",
    "https://uat.e-auction.api.nextpro.io",
    "https://uat-new.e-auction.admin.nextpro.io",
    "https://uat-new.e-auction.user.nextpro.io",
    "https://uat-new.e-auction.api.nextpro.io",
)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    # Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "channels",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "graphene_django",
    "django_cleanup",
    # modules
    "apps.authentication",
    "apps.master_data",
    "apps.users",
    "apps.auctions",
    "apps.realtime",
    "apps.user_guide",
    "apps.sale_schema",
    "apps.payment",
    "apps.invoices",
    "apps.manage_data",
    "apps.rfx",
    "apps.banner",
    "apps.gallery",
    "apps.delivery",
    'django.contrib.humanize',
    'apps.order',
]
CORS_ORIGIN_ALLOW_ALL = True 
GRAPHENE = {
    "SCHEMA": "apps.schema.schema",
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # 3rd party CORS
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "project.middleware.middleware.LanguageMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR + "/templates",
        ],
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

ASGI_APPLICATION = "project.routing.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': os.environ.get('DB_NAME', 'QLDA'),
        "USER": os.environ.get('DB_USER', 'some_user'),
        "PASSWORD": os.environ.get('DB_PASSWORD', 'some_password'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5436'),
        "ATOMIC_REQUESTS": True,
    }

    # "default": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     'NAME': os.environ.get('DB_NAME', 'next-auction'),
    #     "USER": os.environ.get('DB_USER', 'postgres'),
    #     "PASSWORD": os.environ.get('DB_PASSWORD', 'admin123'),
    #     'HOST': os.environ.get('DB_HOST', '172.30.48.1'),
    #     "PORT": os.environ.get('DB_PORT', '5432'),
    #     "ATOMIC_REQUESTS": True,
    # }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": ("apps.authentication.authentication.TokenOverride",),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587  
EMAIL_HOST_USER = "trangiabao433@gmail.com"
EMAIL_HOST_PASSWORD = "bgpw sugy yrqn aewa"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  

STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'),)

DOC_TEMPLATES_DIRS = os.path.join(BASE_DIR, 'templates/')
DOC_GENERATED_DIRS = os.path.join(BASE_DIR, 'documents/')
IMPORT_DIRS = os.path.join(BASE_DIR, 'import/')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CELERY_IMPORTS = ('apps.users', 'apps.auctions', 'apps.payment')

RABBITMQ_URL = os.environ.setdefault('RABBITMQ_URL', 'amqp://rabbitmq')
# RABBITMQ_URL = os.environ.setdefault('RABBITMQ_URL', 'amqp://127.0.0.1')


EINVOICE_URL = os.environ.get('EINVOICE_URL', "http://103.98.160.50/")
EINVOICE_USERNAME = os.environ.get('EINVOICE_USERNAME', "0316185082_test")
EINVOICE_PASSWORD = os.environ.get('EINVOICE_PASSWORD', "12345678")


CELERY_LOADER = 'service.customize.loaders.CustomLoader'
os.environ['CELERY_LOADER'] = CELERY_LOADER
