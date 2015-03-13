from .base import *

INSTALLED_APPS += ('debug_toolbar', 'django.contrib.webdesign')
# ALLOWED_HOSTS = ["*"]
# DEBUG = False
# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
        }
}
ENABLE_RECAPTCHA = True
