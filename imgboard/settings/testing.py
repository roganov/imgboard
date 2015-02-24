from .base import *
INSTALLED_APPS += ('django_nose', 'mock')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
        }
}