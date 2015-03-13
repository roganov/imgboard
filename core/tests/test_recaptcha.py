import unittest
from urllib2 import URLError
from django.test.utils import override_settings
import mock

from django import forms
from django import test
from core import recaptcha

from ..recaptcha import ReCaptchaField


class CapForm(forms.Form):
    captcha = ReCaptchaField()

@override_settings(ENABLE_RECAPTCHA=True)
class TestRecaptchaField(test.SimpleTestCase):
    @mock.patch.object(recaptcha, 'verify', return_value=True)
    def test_valid(self, m_verify):
        f = CapForm({'g-recaptcha-response': 'response-value'})
        self.assertTrue(f.is_valid())
        m_verify.assert_called_with('response-value')

    @mock.patch.object(recaptcha, 'verify', return_value=False)
    def test_valid(self, m_verify):
        f = CapForm({'g-recaptcha-response': 'response-value'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors.as_data()['captcha'][0].code, 'invalid')
        m_verify.assert_called_with('response-value')

    @mock.patch.object(recaptcha, 'verify', side_effect=URLError('reason'))
    def test_error(self, m_verify):
        f = CapForm({'g-recaptcha-response': 'response-value'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors.as_data()['captcha'][0].code, 'error')
        m_verify.assert_called_with('response-value')
