from django import forms

from ipware.ip import get_real_ip
from .models import Post, Thread

class ThreadForm(forms.ModelForm):
    image = forms.ImageField(required=True)
    class Meta:
        model = Thread
        fields = ('title', 'name', 'image', 'raw_body', 'ip')

    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None)
        self.request = kwargs.pop('request', None)
        super(ThreadForm, self).__init__(*args, **kwargs)

    def clean_ip(self):
        return get_real_ip(self.request)

    def save(self):
        return Thread.objects.create(board=self.board, **self.cleaned_data)


class PostForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Post
        fields = ('title', 'name', 'image', 'raw_body', 'ip')

    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop('thread', None)
        self.request = kwargs.pop('request', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def clean_ip(self):
        return get_real_ip(self.request)

    def save(self):
        return Post.objects.create(thread=self.thread, **self.cleaned_data)
