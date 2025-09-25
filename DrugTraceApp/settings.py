"""
Django settings for DrugTraceApp project - PRODUCTION SECURITY CONFIGURATION

This configuration includes enterprise-grade security measures for
pharmaceutical industry compliance and data protection.
"""

from pathlib import Path
import os
import secrets
import string

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# SECURITY CONFIGURATION
# ================================

# Generate a secure secret key for production
def generate_secret_key():
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(64))

# SECURITY WARNING: Use environment variable in production!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', generate_secret_key())

# SECURITY WARNING: Set DEBUG = False in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Production-ready allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    # Add your production domain here
    # 'pharmatrace.com',
    # 'www.pharmatrace.com',
]

# Security Headers and HTTPS Settings
SECURE_SSL_REDIRECT = not DEBUG  # Redirect HTTP to HTTPS in production
SECURE_HSTS_SECONDS = 31536000   # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

# Session Security
SESSION_COOKIE_SECURE = not DEBUG    # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True       # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'   # CSRF protection
SESSION_COOKIE_AGE = 1800            # 30 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# CSRF Security
CSRF_COOKIE_SECURE = not DEBUG       # HTTPS only in production
CSRF_COOKIE_HTTPONLY = True          # No JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'      # Additional protection
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    # Add your production domains here
    # 'https://pharmatrace.com',
]

# Content Security Policy
CSP_DEFAULT_SRC = "'self'"
CSP_SCRIPT_SRC = "'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com"
CSP_STYLE_SRC = "'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com"
CSP_FONT_SRC = "'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com"
CSP_IMG_SRC = "'self' data:"
CSP_CONNECT_SRC = "'self'"
CSP_FRAME_ANCESTORS = "'none'"


# ================================
# APPLICATION DEFINITION
# ================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'traceability',
]

MIDDLEWARE = [
    # Security middleware (order matters!)
    'django.middleware.security.SecurityMiddleware',
    'traceability.middleware.SecurityMiddleware',           # Custom security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'traceability.middleware.SessionSecurityMiddleware',    # Session security
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'traceability.middleware.CSRFProtectionMiddleware',     # Enhanced CSRF
    'traceability.middleware.InputValidationMiddleware',    # Input validation
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DrugTraceApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'DrugTraceApp.wsgi.application'


# ================================
# DATABASE CONFIGURATION
# ================================

# Production database should use PostgreSQL or MySQL with encryption
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # Production PostgreSQL configuration (uncomment for production):
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': os.environ.get('DB_NAME', 'pharmatrace_db'),
        # 'USER': os.environ.get('DB_USER', 'pharmatrace_user'),
        # 'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        # 'HOST': os.environ.get('DB_HOST', 'localhost'),
        # 'PORT': os.environ.get('DB_PORT', '5432'),
        # 'OPTIONS': {
        #     'sslmode': 'require',  # Require SSL connection
        # },
    }
}

# Database connection pooling and security
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================================
# PASSWORD VALIDATION & SECURITY
# ================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.7,  # More strict similarity check
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Pharmaceutical industry standard
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Custom pharmaceutical industry password validator
    {
        'NAME': 'traceability.validators.PharmaceuticalPasswordValidator',
    },
]

# Account lockout settings
ACCOUNT_LOCKOUT_ON_FAILURE = True
ACCOUNT_LOCKOUT_TIME = 1800  # 30 minutes
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes

# Password complexity requirements
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True  
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SYMBOLS = True


# ================================
# LOGGING CONFIGURATION
# ================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {levelname} {asctime} - {message} - {pathname}:{lineno}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'pharmatrace.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO' if DEBUG else 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'pharmatrace.security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# ================================
# FILE UPLOAD SECURITY
# ================================

# File upload settings with security constraints
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
FILE_UPLOAD_PERMISSIONS = 0o644

# Allowed file types for pharmaceutical documentation
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.txt', '.doc', '.docx']
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Media files security
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ================================
# STATIC FILES SECURITY
# ================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files security headers
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# ================================
# EMAIL SECURITY (for notifications)
# ================================

# Email backend for security notifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'PharmTrace Security <security@pharmatrace.com>'

# Security notification settings
SECURITY_EMAIL_RECIPIENTS = [
    'admin@pharmatrace.com',
    'security@pharmatrace.com',
]

# ================================
# CACHE SECURITY
# ================================

# Use Redis in production for better security and performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pharmatrace-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Cache security
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'pharmatrace'

# ================================
# INTERNATIONALIZATION & TIMEZONE
# ================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ================================
# CUSTOM SECURITY SETTINGS
# ================================

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# API security (if implementing API endpoints)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Pharmaceutical compliance settings
PHARMACEUTICAL_COMPLIANCE = {
    'REQUIRE_AUDIT_TRAIL': True,
    'REQUIRE_DIGITAL_SIGNATURE': True,
    'DATA_RETENTION_YEARS': 7,
    'REQUIRE_BATCH_TRACKING': True,
    'ENABLE_SERIALIZATION': True,
}

# Security monitoring
SECURITY_MONITORING = {
    'ENABLE_LOGIN_MONITORING': True,
    'ENABLE_FAILED_LOGIN_ALERTS': True,
    'ENABLE_SUSPICIOUS_ACTIVITY_DETECTION': True,
    'ALERT_EMAIL_THRESHOLD': 5,  # Failed attempts before email alert
}

# Environment-specific settings
if not DEBUG:
    # Production-only settings
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
