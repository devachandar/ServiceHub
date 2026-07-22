"""
Django settings for the Payment Service.
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-secret-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "payments",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = []
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get(
            "DATABASE_URL",
            "postgres://servicehub:servicehub@postgres:5432/payment_db",
        )
    )
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "payments.jwt_auth.StatelessJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "payments.exceptions.friendly_exception_handler",
}

JWT_ACCESS_SECRET = os.environ.get("JWT_ACCESS_SECRET", "dev-only-jwt-secret-change-me")
JWT_ACCESS_TTL_MINUTES = int(os.environ.get("JWT_ACCESS_TTL_MINUTES", "15"))
JWT_REFRESH_TTL_DAYS = int(os.environ.get("JWT_REFRESH_TTL_DAYS", "7"))

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://servicehub:servicehub@rabbitmq:5672//")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_DEFAULT_RETRY_DELAY = 10

INTERNAL_SERVICE_URLS = {
    "auth": os.environ.get("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "user": os.environ.get("USER_SERVICE_URL", "http://user-service:8002"),
    "provider": os.environ.get("PROVIDER_SERVICE_URL", "http://provider-service:8003"),
    "booking": os.environ.get("BOOKING_SERVICE_URL", "http://booking-service:8004"),
    "review": os.environ.get("REVIEW_SERVICE_URL", "http://review-service:8005"),
    "payment": os.environ.get("PAYMENT_SERVICE_URL", "http://payment-service:8006"),
    "search": os.environ.get("SEARCH_SERVICE_URL", "http://search-service:8007"),
    "media": os.environ.get("MEDIA_SERVICE_URL", "http://media-service:8009"),
}
