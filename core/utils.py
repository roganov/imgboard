from PIL import Image
from cStringIO import StringIO

from django.core.files.base import File

def get_thumbnail(original_img, thumbnail_size=(250, 250)):
    """Takes an image of a `File` class (such as InMemoryUploadedFile in request.FILES)
       and returns the thumbnailed image wrapped in `File`"""
    img_file = original_img.file
    image = Image.open(img_file)
    image.thumbnail(thumbnail_size, Image.ANTIALIAS)
    temp = StringIO()
    image.save(temp, image.format)
    return File(temp)