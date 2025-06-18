from pathlib import Path

import redis.asyncio as redis
from chatme.installed import INSTALLED_APPS
from decouple import config

from . import redis_conf

BASE_DIR = Path(__file__).resolve().parent.parent.parent

REPO_DIR = BASE_DIR.parent

TEMPLATES_DIR = BASE_DIR / "templates"

SECRET_KEY = config("CHATME_SECRET", cast=str)

ASGI_APPLICATION = "chatme.asgi.application"

INSTALLED_APPS = INSTALLED_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATES_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

if database_url := config("DATABASE_URL", cast=str, default=""):
    import dj_database_url

    if database_url.startswith("postgres://") or database_url.startswith(
        "postgresql://"
    ):
        DATABASES = {
            "default": dj_database_url.config(
                default=database_url,
            )
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# # Django Channels Layer (using in-memory for now, Redis will be in Phase 2)
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer",
#     }
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config("CHANNEL_LAYERS_HOST", default="")],
            "symmetric_encryption_keys": [config("CHATME_SECRET")],
        },
    }
}

# CACHES
if cache_url := config("REDIS_URL_CACHE", default=""):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": cache_url,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": redis_conf.get_redis_params()["password"],
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# SESSION_ENGINE + SESSION_REDIS
SESSION_ENGINE = "redis_sessions.session"
SESSION_REDIS = {
    **redis_conf.get_redis_params(db=2),
    "prefix": "chatme:session",
    "socket_timeout": 1,
}

REDIS_CLIENT = redis.Redis(
    **redis_conf.get_redis_params(db=2),
    decode_responses=True,
    protocol=3,
)


ROOT_URLCONF = "chatme.urls"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LOGIN_REDIRECT_URL = "chats/"

STATIC_URL = "static/"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
