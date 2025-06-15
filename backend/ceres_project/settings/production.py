"""
Production settings for CERES project
Settings for Railway.app and other production environments
"""
from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts for production
ALLOWED_HOSTS = [
    '.railway.app',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# Add custom domain if provided
CUSTOM_DOMAIN = config('CUSTOM_DOMAIN', default='')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# Database configuration for production (Railway PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Cache configuration for production (Redis)
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'ceres',
        'TIMEOUT': 3600,  # 1 hour default
    }
}

# Channel layers for WebSocket (production)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "https://your-app.railway.app",
]

# Add custom frontend domain if provided
FRONTEND_URL = config('FRONTEND_URL', default='')
if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)

CORS_ALLOW_CREDENTIALS = True

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@ceres.com')

# Static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Logging for production
LOGGING['handlers']['file']['filename'] = '/tmp/ceres.log'  # Railway writable path
LOGGING['handlers']['console']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['ceres']['level'] = 'INFO'

# Production-specific CERES settings
CERES_SETTINGS.update({
    'OCR_TESSERACT_CMD': '/usr/bin/tesseract',
    'SCREENING_SOURCES': {
        'ofac': {
            'enabled': config('OFAC_ENABLED', default=True, cast=bool),
            'cache_hours': config('OFAC_CACHE_HOURS', default=24, cast=int),
        },
        'un': {
            'enabled': config('UN_ENABLED', default=True, cast=bool),
            'cache_hours': config('UN_CACHE_HOURS', default=24, cast=int),
        },
        'eu': {
            'enabled': config('EU_ENABLED', default=True, cast=bool),
            'cache_hours': config('EU_CACHE_HOURS', default=24, cast=int),
        },
        'opensanctions': {
            'enabled': config('OPENSANCTIONS_ENABLED', default=True, cast=bool),
            'cache_hours': config('OPENSANCTIONS_CACHE_HOURS', default=24, cast=int),
            'api_key': config('OPENSANCTIONS_API_KEY', default=''),
        },
    },
    'ALERT_SETTINGS': {
        'websocket_enabled': config('WEBSOCKET_ALERTS_ENABLED', default=True, cast=bool),
        'email_enabled': config('EMAIL_ALERTS_ENABLED', default=True, cast=bool),
        'sms_enabled': config('SMS_ALERTS_ENABLED', default=False, cast=bool),
    }
})

# Celery configuration for production
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery beat schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'update-screening-sources': {
        'task': 'sanctions_screening.tasks.update_all_screening_sources',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-old-alerts': {
        'task': 'core.tasks.cleanup_old_alerts',
        'schedule': 86400.0,  # Daily
    },
    'generate-daily-reports': {
        'task': 'sanctions_screening.tasks.generate_daily_reports',
        'schedule': 86400.0,  # Daily
    },
}

# Performance optimizations for production
DATABASE_CONN_MAX_AGE = 600
CONN_HEALTH_CHECKS = True

# File upload limits for production
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour

# Admin security
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Monitoring and health checks
HEALTH_CHECK_ENABLED = config('HEALTH_CHECK_ENABLED', default=True, cast=bool)

