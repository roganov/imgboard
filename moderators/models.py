from django.conf import settings
from django.db import models, transaction
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ModeratorActionManager(models.Manager):
    # dispatcher
    def create_action(self, *args, **kwargs):
        action = kwargs['action']
        method = getattr(self, 'create_{}'.format(action))
        return method(*args, **kwargs)

    @transaction.atomic
    def create_close(self, *args, **kwargs):
        kwargs['action'] = 'close'
        mod_action = self.create(*args, **kwargs)
        mod_action.content_object.is_closed = True
        mod_action.content_object.save()
        return mod_action

    @transaction.atomic
    def create_pin(self, *args, **kwargs):
        kwargs['action'] = 'pin'
        mod_action = self.create(*args, **kwargs)
        mod_action.content_object.is_pinned = True
        mod_action.content_object.save()
        return mod_action

    @transaction.atomic
    def create_delete(self, *args, **kwargs):
        kwargs['action'] = 'delete'
        mod_action = self.create(*args, **kwargs)
        mod_action.content_object.is_hidden = True
        mod_action.content_object.save()
        return mod_action

    # @transaction.atomic
    # transaction is disabled because images deletion can be slow
    # and we don't want the transaction to hang
    # FIXME: deletion may throw exceptions
    def create_delete_img(self, *args, **kwargs):
        kwargs['action'] = 'delete_img'
        mod_action = self.create(*args, **kwargs)
        mod_action.content_object.image.delete(save=False)
        mod_action.content_object.thumbnail.delete(save=False)
        mod_action.content_object.save()
        return mod_action

    @transaction.atomic
    def create_ban(self, *args, **kwargs):
        kwargs['action'] = 'ban'
        until = kwargs.pop('until')
        ip = kwargs['content_object'].ip
        mod_action = self.create(*args, **kwargs)
        ban = Ban.objects.create(action=mod_action, ip=ip, until=until)
        return mod_action


class ModeratorAction(models.Model):
    ACTION_CHOICES = (
        ('close', 'Close the thread'),
        ('pin', 'Pin the thread'),
        ('delete', 'Delete this thread or post'),
        ('delete_img', 'Delete img'),
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

    # manager
    objects = ModeratorActionManager()

    def __unicode__(self):
        return "<ModeratorAction: {}>".format(self.action)


class Ban(models.Model):
    action = models.ForeignKey(ModeratorAction)
    ip = models.GenericIPAddressField(db_index=True)
    until = models.DateTimeField()

    def __unicode__(self):
        return "<Ban: {}>".format(self.ip)