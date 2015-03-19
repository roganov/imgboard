from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save

class CoreConfig(AppConfig):
    name = 'core'
    def ready(self):
        if getattr(settings, 'ENABLE_LIVE_UPDATES', False):
            from .signals import publish_post
            post_save.connect(publish_post, sender=self.get_model('Post'))
