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
seen = set()
INSTALLED_APPS = [x for x in INSTALLED_APPS if not(x in seen or seen.add(x))]