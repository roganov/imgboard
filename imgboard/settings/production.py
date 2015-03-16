from .base import *
import os
import dj_database_url

DEBUG = os.environ.get('DEBUG', False)

INSTALLED_APPS += ('storages',)

DATABASES = {'default': dj_database_url.config()}

ALLOWED_HOSTS = ["*"]

# templates are cached in production
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# S3 settings
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = 'imgboard-bucket-2'
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Cache-Control': 'max-age=31556926'
}
MEDIA_URL = 'http://imgboard-bucket-2.s3-eu-west-1.amazonaws.com/'

ENABLE_RECAPTCHA = True
RECAPTCHA_KEY = os.environ['RECAPTCHA_KEY']