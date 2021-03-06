from functools import wraps
import json
from urllib import urlencode
import urllib2

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

verify_url = 'https://www.google.com/recaptcha/api/siteverify'
def verify(response):
    secret = settings.RECAPTCHA_KEY
    resp = urllib2.urlopen(verify_url, urlencode({
        'secret': secret,
        'response': response
    })).read()
    return json.loads(resp)['success']

class ReCaptchaWidget(forms.widgets.Widget):
    g_nocaptcha_response = 'g-recaptcha-response'

    def value_from_datadict(self, data, files, name):
        return data.get(self.g_nocaptcha_response)

class ReCaptchaField(forms.CharField):
    widget = ReCaptchaWidget
    default_error_messages = {
        'invalid': _('Incorrect, please try again'),
        'error': _('Something went wrong')
    }

    def clean(self, value):
        if not settings.ENABLE_RECAPTCHA:
            return value
        try:
            ok = verify(value)
        except urllib2.URLError:
            code = 'error'
            raise ValidationError(self.default_error_messages[code], code=code)
        if not ok:
            code = 'invalid'
            raise ValidationError(self.default_error_messages[code], code=code)
        return value

def captcha_every_n(f):
    enabled = settings.ENABLE_RECAPTCHA
    INTERVAL = settings.CAPTCHA_EVERY_N
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        response = f(request, *args, **kwargs)
        if request.method == 'POST' and enabled:
            bc = request.session.get('posts_before_captcha', 0)
            if bc <= 0:
                request.session['posts_before_captcha'] = new_bc = INTERVAL - 1
            else:
                request.session['posts_before_captcha'] = new_bc = bc - 1
            response.set_cookie('captcha', 1 if new_bc == 0 else 0)
        if not enabled:
            response.set_cookie('captcha', 0)
        elif 'captcha' not in request.COOKIES:
            response.set_cookie('captcha', 1)
        return response
    return wrapper