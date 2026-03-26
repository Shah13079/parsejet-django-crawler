"""Django settings for the crawler project."""
import os
from pathlib import Path
from decouple import config
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = ['127.0.0.1', '127.0.0.1:8000', 'scrapysoft.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'amazon_crawler',
    'accounts',
    'debug_toolbar',
    'django_celery_results',
    'django_celery_beat',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crawler.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'crawler.wsgi.application'
ASGI_APPLICATION = 'crawler.asgi.application'
AUTH_USER_MODEL = 'accounts.Account'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Email used by error-alert emails sent from the scraping engines
TECH_ADMIN_EMAIL = config('TECH_ADMIN_EMAIL')

# SMTP configuration for outgoing emails (activation, password reset, job status)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Zyte (formerly Crawlera) proxy credentials for Amazon scraping
PROXY_HOST = config('EMAIL_HOST_USER')
PROXY_PORT = config('PROXY_PORT')
PROXY_AUTH = config('PROXY_AUTH')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'amazon_crawler/static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    '127.0.0.1',
]

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    50: 'critical',
}

# Celery configuration (local Redis broker)
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Karachi'

# Celery Beat scheduler backed by Django database
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'