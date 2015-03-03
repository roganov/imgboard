from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ModeratorAction(models.Model):
    ACTION_CHOICES = (
        ('close', 'Close the thread'),
        ('delete', 'Delete this thread or post'),
        ('del_img', 'Delete img'),
        ('ban', 'Ban the author'),
    )
    action = models.CharField(max_length=100,
                              choices=ACTION_CHOICES)

    content_type = models.ForeignKey(ContentType)
    ref_obj_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'ref_obj_id')

    moderator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    def __unicode__(self):
        return "<ModeratorAction: {}>".format(self.action)


class Ban(models.Model):
    action = models.ForeignKey(ModeratorAction)
    ip = models.GenericIPAddressField(db_index=True)
    until = models.DateTimeField()

    def __unicode__(self):
        return "<Ban: {}>".format(self.ip)