# -*- encoding: utf-8 -*-
import os
import ast
import dj_database_url

# To parse REDIS_URL
from urllib.parse import urlparse

"""
Django settings for RexChain project.

Generated by 'django-admin startproject' using Django 1.11.3. (oldddddd)

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.environ['DATABASE_URL']
DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ast.literal_eval(os.environ['DEBUG_STATE'])

# RM Autofield warning by setting a global config
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Check if we are in production
PRODUCTION = ast.literal_eval(os.environ['PRODUCTION'])
# Change allowed hosts accordingly
if PRODUCTION:
    ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS']]
else:
    ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS'], os.environ['HEROKU_APP_NAME']+".herokuapp.com", "127.0.0.1"]

# SSL
SESSION_COOKIE_SECURE = ast.literal_eval(os.environ['SECURE_SSL_REDIRECT'])
CSRF_COOKIE_SECURE = ast.literal_eval(os.environ['SECURE_SSL_REDIRECT'])
SECURE_SSL_REDIRECT = ast.literal_eval(os.environ['SECURE_SSL_REDIRECT'])
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

BLOCK_SIZE = int(os.environ["BLOCK_SIZE"])

# NOM151 Reachcore env vars
REACHCORE_ENTITY = os.environ["REACHCORE_ENTITY"]
REACHCORE_USER = os.environ["REACHCORE_USER"]
REACHCORE_PASS = os.environ["REACHCORE_PASS"]

# JIRA SETTINGS
JIRA_URL = os.environ["JIRA_URL"]
JIRA_USER = os.environ["JIRA_USER"]
JIRA_PASSWORD = os.environ["JIRA_PASSWORD"]

# Proof of existence specific (interface with external ledger)
BLOCKCYPHER_API_TOKEN = os.environ['BLOCKCYPHER_API_TOKEN']
CHAIN = os.environ['CHAIN']
BASE_POE_URL = os.environ['BASE_POE_URL']
STAMPD_ID = os.environ['STAMPD_ID']
STAMPD_KEY = os.environ['STAMPD_KEY']

# Hashcash settings
HC_BITS_DIFFICULTY = os.environ["HC_BITS_DIFFICULTY"]
HC_RANDOM_STRING_SIZE = os.environ["HC_RANDOM_STRING_SIZE"]
HC_WORD_INITIAL = os.environ['HC_WORD_INITIAL']

# WALLET_URL
WALLET_URL = os.environ["WALLET_URL"]
# WHITEPAPER_URL
WHITEPAPER_URL = os.environ["WHITEPAPER_URL"]

# Django JET config
JET_SIDE_MENU_COMPACT = True

APPEND_SLASH = True

# Application definition
INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_rq',
    'api',
    'blockchain',
    'core',
    'nom151',
    # CORS
    'corsheaders',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # CORS Middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS configuration
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'rexchain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'rexchain.processors.add_production_var',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rexchain.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 15,
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.TokenAuthentication',
    )
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Fixtures DIR for testings
FIXTURE_DIRS = [os.path.join(BASE_DIR, 'fixtures')]

# Define REDIS_URL
REDIS_URL = os.getenv("REDIS_URL", 'redis://localhost:6379/0')
# Redis Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                    #  config for pool connections
                    "max_connections": 10 # Note, we should review this.
            }
        }
    }
}

# Parsing URL in order to single out TSL connections
parsed_url = urlparse(REDIS_URL)

# Append SSL/TLS configuration if using rediss:// (TLS)
if parsed_url.scheme == 'rediss':
    CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS'].update({
        'ssl_cert_reqs': None  # or ssl.CERT_REQUIRED with proper CA certs
    })

# Redis Config
RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
    },
    'high': {
        'USE_REDIS_CACHE': 'default',
    },
    'low': {
        'USE_REDIS_CACHE': 'default',
    }
}

# extra config args for RQ
RQ = {
    # RQ_EXCEPTION_HANDLERS = ['']
}

# Console logging for DEBUG=False - Probably should disable if DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {  # add rq_console format
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        "rq_console": {  # add rq_console hadler
            "level": os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            "class": "logging.StreamHandler",
            "formatter": "rq_console",
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'loggers': {
        'django_info': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        "rq.worker": {  # add rq logger
            "handlers": ["rq_console"],
            "level": os.getenv('DJANGO_LOG_LEVEL', 'INFO')
        },
    },
}
