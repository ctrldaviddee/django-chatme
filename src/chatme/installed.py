DJANGO_INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "redis_sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_INSTALLED_APPS = [
    "channels",
    "django_cleanup.apps.CleanupConfig",
    "django_htmx",
    "allauth",
    "allauth.account",
    "debug_toolbar",
    "django_tailwind_cli",
]

MY_APPS = [
    "core",
    "home",
    "users",
    "chats",
]

INSTALLED_APPS = [
    "daphne",
    *DJANGO_INSTALLED_APPS,
    *THIRD_PARTY_INSTALLED_APPS,
    *MY_APPS,
]

# Remove duplicates from while preserving order
INSTALLED_APPS = list(dict.fromkeys(INSTALLED_APPS))
