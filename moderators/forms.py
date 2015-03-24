from django import forms
from django.forms import ValidationError
from core.models import Thread, Post
from .models import ModeratorAction, Ban

class ModActionForm(forms.ModelForm):
    until = forms.DateTimeField(required=False)
    content_object = forms.CharField(required=True)

    class Meta:
        model = ModeratorAction
        fields = ['action', 'reason']

    def __init__(self, *args, **kwargs):
        self.moderator = kwargs.pop('user', None)
        super(ModActionForm, self).__init__(*args, **kwargs)

    def clean_moderator(self):
        return self.moderator

    def clean_content_object(self):
        obj_id = self.cleaned_data['content_object']
        if obj_id[0] == 't':
            get = Thread.objects.select_related('board').get
            id_ = obj_id[1:]
        else:
            get = Post.objects.select_related('thread__board').get
            id_ = obj_id
        try:
            obj = get(pk=id_)
        except (Thread.DoesNotExist, Post.DoesNotExist):
            raise ValidationError("Related object not found")

        if not obj.board.moderators.filter(pk=self.moderator.pk).exists():
            raise ValidationError(
                "You are not authorized to perform this action")
        return obj

    def clean(self):
        cleaned_data = super(ModActionForm, self).clean()
        cleaned_data['moderator'] = self.moderator
        action = cleaned_data.get('action')
        obj = cleaned_data.get('content_object')
        if action == 'ban' and obj:
            if 'until' not in cleaned_data:
                raise ValidationError("You must set `until` date")
            if not obj.ip:
                raise ValidationError("The object does not have IP field")
        else:
            del cleaned_data['until']

        if action in ('close', 'pin') and obj and not isinstance(obj, Thread):
            raise ValidationError("Only threads can be closed or pinned")

    def save(self):
        return ModeratorAction.objects.create_action(**self.cleaned_data)
