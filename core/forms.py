from django import forms
from .models import Post, Thread

class ThreadForm(forms.ModelForm):
    image = forms.ImageField(required=True)
    class Meta:
        model = Thread
        fields = ('title', 'name', 'image', 'raw_body')

    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None)
        super(ThreadForm, self).__init__(*args, **kwargs)

    def save(self):
        return Thread.objects.create(board=self.board, **self.cleaned_data)


class PostForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Post
        fields = ('title', 'name', 'image', 'raw_body')

    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop('thread', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self):
        return Post.objects.create(thread=self.thread, **self.cleaned_data)