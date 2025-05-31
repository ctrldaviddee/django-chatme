DJANGO_INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_INSTALLED_APPS = [
]

MY_APPS = [

]

INSTALLED_APPS = [
    'daphne',
    *DJANGO_INSTALLED_APPS,
    *THIRD_PARTY_INSTALLED_APPS,
    *MY_APPS,
]

# Remove duplicates from while preserving order
INSTALLED_APPS = list(dict.fromkeys(INSTALLED_APPS))