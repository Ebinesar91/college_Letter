"""
Django settings for Smart College Permission Management System.
Production-ready for Vercel + PostgreSQL (Supabase/Neon).
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import django.template.context as context_mod

# ── Python 3.14 Compatibility Patch for Django 5.1 ──
def base_context_copy_patch(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate

context_mod.BaseContext.__copy__ = base_context_copy_patch


# ═══════════════════════════════════════════════════════
# CORE SETTINGS
# ═══════════════════════════════════════════════════════

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Secret Key ──
# NEVER use the fallback insecure key in production.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('DEBUG', 'True') == 'True':
        SECRET_KEY = 'django-insecure-dev-only-cpms-secret-DO-NOT-USE-IN-PROD'
    else:
        raise ImproperlyConfigured(
            "SECRET_KEY environment variable is MISSING. "
            "Set it in Vercel dashboard → Settings → Environment Variables."
        )

# ── Debug Mode ──
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ── Allowed Hosts ──
# In production, set ALLOWED_HOSTS to your Vercel domain(s).
# Example: "your-app.vercel.app,.your-custom-domain.com"
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    _hosts = os.environ.get('ALLOWED_HOSTS', '')
    if not _hosts:
        raise ImproperlyConfigured(
            "ALLOWED_HOSTS environment variable is MISSING in production. "
            "Set it to your Vercel domain, e.g. 'your-app.vercel.app'"
        )
    ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]

# Also set CSRF_TRUSTED_ORIGINS for Vercel
CSRF_TRUSTED_ORIGINS = [
    f'https://{host}' for host in ALLOWED_HOSTS if host != '*'
]
# Add common Vercel patterns
_vercel_url = os.environ.get('VERCEL_URL')
if _vercel_url:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_vercel_url}')


# ═══════════════════════════════════════════════════════
# APPLICATIONS & MIDDLEWARE
# ═══════════════════════════════════════════════════════

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'permissions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'permissions.middleware.RoleBasedAccessMiddleware',
]

ROOT_URLCONF = 'college_permission_system.urls'

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

WSGI_APPLICATION = 'college_permission_system.wsgi.application'


# ═══════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════
# Priority:
#   1. DATABASE_URL env var → PostgreSQL (production)
#   2. POSTGRES_URL env var → PostgreSQL (Vercel Postgres)
#   3. DEBUG=True → SQLite (local development only)
#   4. DEBUG=False + no URL → CRASH with clear error

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
    # Force PostgreSQL engine (prevent any SQLite fallback)
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
elif DEBUG:
    # Local development only
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    raise ImproperlyConfigured(
        "\n╔══════════════════════════════════════════════════════════╗\n"
        "║  FATAL: No DATABASE_URL found in production!            ║\n"
        "║                                                         ║\n"
        "║  Vercel does NOT support SQLite (read-only filesystem). ║\n"
        "║                                                         ║\n"
        "║  Set DATABASE_URL in Vercel Environment Variables:      ║\n"
        "║  → Settings → Environment Variables → DATABASE_URL      ║\n"
        "║  → Use Supabase or Neon PostgreSQL connection string    ║\n"
        "╚══════════════════════════════════════════════════════════╝"
    )


# ═══════════════════════════════════════════════════════
# PASSWORD VALIDATION
# ═══════════════════════════════════════════════════════

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ═══════════════════════════════════════════════════════
# INTERNATIONALIZATION
# ═══════════════════════════════════════════════════════

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# ═══════════════════════════════════════════════════════
# STATIC FILES (WhiteNoise for Vercel)
# ═══════════════════════════════════════════════════════

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Production: compressed + hashed static files
if not DEBUG:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

# Media: NOT supported on Vercel (read-only filesystem)
# Use a cloud storage (S3/Cloudinary) if you need user uploads.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ═══════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'permissions.CustomUser'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'


# ═══════════════════════════════════════════════════════
# EMAIL (Gmail SMTP)
# ═══════════════════════════════════════════════════════
# All credentials pulled from environment variables.
# NEVER hardcode passwords in source code.

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'Smart CPMS Admin <noreply@smartcpms.edu>'
)


# ═══════════════════════════════════════════════════════
# SESSION & CSRF SECURITY
# ═══════════════════════════════════════════════════════

SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# ── Production-only security hardening ──
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000          # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'


# ═══════════════════════════════════════════════════════
# CACHING
# ═══════════════════════════════════════════════════════

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# ═══════════════════════════════════════════════════════
# LOGIN RATE LIMITING
# ═══════════════════════════════════════════════════════

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15


# ═══════════════════════════════════════════════════════
# PASSWORD RESET
# ═══════════════════════════════════════════════════════

PASSWORD_RESET_TIMEOUT = 3600  # 1 hour


# ═══════════════════════════════════════════════════════
# LOGGING (useful for debugging Vercel deployments)
# ═══════════════════════════════════════════════════════

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
