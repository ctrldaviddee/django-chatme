from decouple import config

from .base import *  # noqa: F403 F401

DEBUG = config("DEBUG")

# TODO: Update with actual production hosts
ALLOWED_HOSTS = []

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True
