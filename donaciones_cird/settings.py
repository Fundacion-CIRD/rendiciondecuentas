import sys
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = getenv("SECRET_KEY")

DEBUG = getenv("DEBUG").lower() in ("true", "1")

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'active_link',
    'rest_framework',
    'rangefilter',
    'utils',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'donaciones_cird.urls'

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

WSGI_APPLICATION = 'donaciones_cird.wsgi.application'


DEFAULT_DATABASE = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": getenv("DB_NAME"),
    "USER": getenv("DB_USER"),
    "PASSWORD": getenv("DB_PASSWORD"),
    "HOST": getenv("DB_HOST"),
    "PORT": getenv("DB_PORT"),
}

TEST_DATABASE = {
    "ENGINE": "django.db.backends.sqlite3",
    "TEST_CHARSET": "UTF8",
    "NAME": "file:default?mode=memory",
    "OPTIONS": {
        "timeout": 30,
    },
}


IS_TEST = "pytest" in sys.argv[0]

DATABASES = {"default": TEST_DATABASE if IS_TEST else DEFAULT_DATABASE}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
        ),
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


LANGUAGE_CODE = 'es-PY'

TIME_ZONE = 'America/Asuncion'

DATE_FORMAT = '%d/%m/%Y'

DATE_INPUT_FORMATS = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%d/%m/%y']

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True


STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_DIRS = [
    BASE_DIR / 'static_compiled',
    BASE_DIR / 'staticfiles',
]


MEDIA_ROOT = BASE_DIR / 'uploads'

MEDIA_URL = '/uploads/'

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'local-cache',
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "console_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": getenv("LOG_LEVEL", "INFO"),
        },
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": [
                # Enable this for logging SQL queries
                # 'console_debug',
            ],
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/sec',
    },
}
