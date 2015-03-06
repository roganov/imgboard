from functools import wraps
from PIL import Image
from cStringIO import StringIO

from django.core.cache import cache
from django.db.models.loading import get_model
from django.db.models.signals import post_save
from django.core.files.base import File
from django.dispatch import receiver
from django.http import HttpResponse


def get_thumbnail(original_img, thumbnail_size=(250, 250)):
    """Takes an image of a `File` class (such as InMemoryUploadedFile in request.FILES)
       and returns the thumbnailed image wrapped in `File`"""
    img_file = original_img.file
    image = Image.open(img_file)
    image.thumbnail(thumbnail_size, Image.ANTIALIAS)
    temp = StringIO()
    image.save(temp, image.format)
    return File(temp)


def cache_board_view(timeout, n_pages):
    """Decorator that caches first `n_pages` pages of the requested board
       Not cached for authenticated users (moderators).
       Also connects to post_save signal to remove affected keys.
    """
    @receiver(post_save, sender=get_model('core', 'Post'), weak=False)
    def expire_affected_keys(sender, instance, **kwargs):
        slug = instance.thread.board.slug
        keys = ['{}:{}'.format(slug, i) for i in range(1, n_pages+1)]
        cache.delete_many(keys)

    def decorator(f):
        @wraps(f)
        def wrapper(request, slug, page=None):
            page_n = int(page or '1')
            if not request.user.is_authenticated() and\
                            request.method == 'GET' and page_n <= n_pages:
                key = '{}:{}'.format(slug, page_n)
                content = cache.get(key)
                if content is None:
                    response = f(request, slug, page)
                    cache.set(key, response.content, timeout)
                else:
                    response = HttpResponse(content)
                return response
            return f(request, slug, page)

        return wrapper
    return decorator
