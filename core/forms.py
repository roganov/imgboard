from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'name', 'raw_body')

    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop('thread', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self):
        return Post.objects.create(thread=self.thread, **self.cleaned_data)
