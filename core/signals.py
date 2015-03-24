from django.conf import settings
from django.template import Context
from django.template.loader import get_template

from redis import StrictRedis, ConnectionPool

POOL = ConnectionPool(**settings.REDIS_CONF)

def publish_post(sender, instance, created, **kwargs):
    """Render new post and sent down the corresponding channel"""
    if not created:
        return
    rs = StrictRedis(connection_pool=POOL)
    channel = 'boards.{}.{}'.format(instance.board.slug, instance.thread_id)

    ctx = {'post': instance}
    rendered_post = get_template('_post.html').render(Context(ctx))

    rs.publish(channel, rendered_post)