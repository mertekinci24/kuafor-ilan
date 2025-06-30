import os
from pathlib import Path
from django.contrib import messages
import os
import sys

# Projenin kök dizinini (manage.py'nin bir üstü) yola ekle
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-kuafor_ilan-test-key-12345')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Allowed hosts
ALLOWED_HOSTS = ['*'] # Üretimde domain isimlerinizi buraya eklemelisiniz
CSRF_TRUSTED_ORIGINS = ['https://kuaforilan.com', 'https://*.kuaforilan.com']

# Application definition
INSTALLED_APPS = [
    'kuafor_ilan',
    'apps.core', # ÖNEMLİ: authentication'dan önce olmalı çünkü CustomUser buradan miras alıyor
    'apps.authentication.apps.AuthenticationConfig', # authentication hala kendi içindeki modeller için öncelikli olmalı
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.dashboard',
    'apps.jobs',
    'apps.profiles',
    'apps.posts',
    'apps.messages.apps.MessagesConfig',
    'apps.notifications.apps.NotificationsConfig',
]

# Authentication settings
AUTH_USER_MODEL = 'authentication.CustomUser'

# Authentication backends - Email ile giriş için
AUTHENTICATION_BACKENDS = [
    'apps.authentication.backends.EmailBackend',  # Custom backend'imiz
    'django.contrib.auth.backends.ModelBackend',  # Varsayılan backend
]

# Login/Logout yönlendirmeleri
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'  # Fallback
LOGOUT_REDIRECT_URL = '/auth/login/'

# User type redirect mapping (Gelecekteki dashboard'lar için)
USER_TYPE_REDIRECT_MAP = {
    'admin': '/admin/',
    'business': '/dashboard/business/',
    'jobseeker': '/posts/',  # Dashboard hazır olunca '/dashboard/jobseeker/' olacak
    'default': '/posts/'
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kuafor_ilan.urls'

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

WSGI_APPLICATION = 'kuafor_ilan.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Ayarları
DEFAULT_FROM_EMAIL = 'noreply@kuaforilan.com'

# OTP ayarları
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5

# Mesaj çerçevesi ayarları
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Session settings
SESSION_COOKIE_AGE = 86400 * 30  # 30 gün
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SMS ve Email ayarları
NETGSM_USERNAME = os.environ.get('NETGSM_USERNAME', '')
NETGSM_PASSWORD = os.environ.get('NETGSM_PASSWORD', '')
NETGSM_HEADER = os.environ.get('NETGSM_HEADER', 'KUAFORILAN')

# Loglama Ayarları
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'ignore_bots': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'bot' not in record.getMessage().lower()
        }
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'error.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins', 'error_file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
            'filters': ['ignore_bots'],
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
            'filters': ['ignore_bots'],
        },
    },
}
