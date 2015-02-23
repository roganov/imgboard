from .base import *

INSTALLED_APPS += ('debug_toolbar', 'django.contrib.webdesign')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
        }
}