"""
WSGI config for imgboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imgboard.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Whitenoise is a library which helps
# to serve static directly from django
# In this case it is used to serve static files on heroku
try:
    from whitenoise.django import DjangoWhiteNoise
    application = DjangoWhiteNoise(application)
except ImportError:
    pass