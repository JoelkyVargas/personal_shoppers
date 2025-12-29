# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:20:25 2025

@author: jvz16
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# (Opcional) Cargar .env en LOCAL sin romper si no tenés librería instalada
# =========================
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv(BASE_DIR / ".env")
except Exception:
    # Si no existe python-dotenv, no pasa nada.
    pass


# =========================
# Core settings (por ENV)
# =========================
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-secret-change-me")
DEBUG = os.environ.get("DEBUG", "False").strip().lower() in ("1", "true", "yes", "on")

# ALLOWED_HOSTS por coma: "127.0.0.1,localhost,tuapp.onrender.com"
_allowed_hosts_raw = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_raw.split(",") if h.strip()]

render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)


# CSRF trusted origins por coma (solo lo usarás en Render con https)
_csrf_trusted_raw = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_trusted_raw.split(",") if o.strip()]


# =========================
# Apps
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "marketplace",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


ROOT_URLCONF = "personal_shoppers.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "personal_shoppers.wsgi.application"


# =========================
# Database
# - Local: sqlite (default)
# - Render: Postgres por DATABASE_URL (cuando lo actives)
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    import dj_database_url

    db = dj_database_url.parse(DATABASE_URL, conn_max_age=600)

    # SOLO Postgres necesita sslmode
    if db.get("ENGINE") in ("django.db.backends.postgresql", "django.db.backends.postgresql_psycopg2"):
        db.setdefault("OPTIONS", {})
        db["OPTIONS"]["sslmode"] = "require"

    DATABASES = {"default": db}

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }



# =========================
# Password validators
# (En prod conviene habilitarlos; por ahora no los cambio si estabas en MVP)
# =========================
AUTH_PASSWORD_VALIDATORS = []


# =========================
# Locale / Time
# =========================
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Costa_Rica"
USE_I18N = True
USE_TZ = True


# =========================
# Static / Media
# =========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # necesario para collectstatic en Render

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# Auth redirects
# =========================
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"


# =========================
# Seguridad mínima en producción
# =========================
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
