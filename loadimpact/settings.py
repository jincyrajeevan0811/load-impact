"""
Django settings for the LoadImpact Unisex Gym project.
"""
import os
from pathlib import Path

from django.contrib.messages import constants as message_constants

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: set DJANGO_SECRET_KEY / DJANGO_DEBUG / DJANGO_ALLOWED_HOSTS in production.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-loadimpact-change-this-key-before-going-live-9f3k2m",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Project apps
    "accounts",
    "gym",
    "members",
    "dashboard",
    "appearance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "loadimpact.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "gym.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "loadimpact.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:post_login"
LOGOUT_REDIRECT_URL = "gym:home"

# Emails (password reset etc.) are printed to the console during development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "LoadImpact Gym <no-reply@loadimpact.local>"

# Bootstrap-friendly message tags
MESSAGE_TAGS = {message_constants.ERROR: "danger"}

# Gym information shown across the website
GYM_INFO = {
    "name": "LoadImpact",
    "tagline": "Unisex Fitness Studio",
    "phone": "+91 98765 43210",
    "email": "info@loadimpact.in",
    "address": "1st Floor, Fitness Plaza, MG Road, Kochi, Kerala",
    "hours_weekday": "5:00 AM – 10:00 PM",
    "hours_weekend": "6:00 AM – 8:00 PM",
    "currency": "₹",
    "instagram": "https://instagram.com/",
    "facebook": "https://facebook.com/",
    "youtube": "https://youtube.com/",
    "upi_id": "loadimpact@upi",
}

# Photos used across the website. Replace any URL with your own gym photos,
# e.g. "/static/img/hero.jpg" after copying the file into static/img/.
# Every image sits on top of an animated gradient, so the design still works if a photo can't load.
_UNSPLASH = "https://images.unsplash.com/{}?auto=format&fit=crop&w={}&q=80"
GYM_IMAGES = {
    "hero": _UNSPLASH.format("photo-1534438327276-14e5300c3a48", 1920),
    "about": _UNSPLASH.format("photo-1571019614242-c5c5dee9f50b", 1000),
    "about_2": _UNSPLASH.format("photo-1517836357463-d25dfeac3438", 800),
    "strength": _UNSPLASH.format("photo-1517836357463-d25dfeac3438", 900),
    "cardio": _UNSPLASH.format("photo-1540497077202-7c8a3999166f", 900),
    "classes": _UNSPLASH.format("photo-1518611012118-696072aa579a", 900),
    "personal": _UNSPLASH.format("photo-1571019614242-c5c5dee9f50b", 900),
    "auth": _UNSPLASH.format("photo-1583454110551-21f2fa2afe61", 1200),
    "page_header": _UNSPLASH.format("photo-1540497077202-7c8a3999166f", 1920),
    "cta": _UNSPLASH.format("photo-1534438327276-14e5300c3a48", 1600),
    "gallery": [
        _UNSPLASH.format("photo-1534438327276-14e5300c3a48", 800),
        _UNSPLASH.format("photo-1540497077202-7c8a3999166f", 800),
        _UNSPLASH.format("photo-1517836357463-d25dfeac3438", 800),
        _UNSPLASH.format("photo-1518611012118-696072aa579a", 800),
        _UNSPLASH.format("photo-1571019614242-c5c5dee9f50b", 800),
        _UNSPLASH.format("photo-1583454110551-21f2fa2afe61", 800),
    ],
}
