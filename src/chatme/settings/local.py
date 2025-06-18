from .base import *  # noqa: F403

DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]

INSTALLED_APPS += ["debug_toolbar", "django_tailwind_cli"]  # noqa: F405

MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
