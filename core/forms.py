from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from ipware.ip import get_real_ip

from misc.recaptcha import ReCaptchaField
from .models import Post, Thread


class WithCaptchaMixin(object):
    def __init__(self, *args, **kwargs):
        self.request = request = kwargs.pop('request', None)
        with_captcha = kwargs.pop('with_captcha', False)
        super(WithCaptchaMixin, self).__init__(*args, **kwargs)
        if request and with_captcha:
            self.fields['captcha'] = ReCaptchaField()

class ThreadForm(WithCaptchaMixin, forms.ModelForm):
    image = forms.ImageField(required=True)
    class Meta:
        model = Thread
        fields = ('title', 'name', 'image', 'raw_body', 'ip')

    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None)
        super(ThreadForm, self).__init__(*args, **kwargs)

    def clean_ip(self):
        return get_real_ip(self.request)

    def save(self):
        self.cleaned_data.pop('captcha', None)
        return Thread.objects.create(board=self.board, **self.cleaned_data)


class PostForm(WithCaptchaMixin, forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Post
        fields = ('title', 'name', 'image', 'raw_body', 'ip')

    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop('thread', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def clean_ip(self):
        return get_real_ip(self.request)

    def clean(self):
        if self.thread.is_closed:
            raise ValidationError(_('The thread is closed'), code='closed')

    def save(self):
        self.cleaned_data.pop('captcha', None)
        return Post.objects.create(thread=self.thread, **self.cleaned_data)
