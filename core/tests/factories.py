import factory

from ..models import Board, Thread, Post


class PostFactory(factory.DjangoModelFactory):
    class Meta:
        model = Post

class ThreadFactory(factory.DjangoModelFactory):
    class Meta:
        model = Thread


class BoardFactory(factory.DjangoModelFactory):
    slug = 'test'
    class Meta:
        model = Board


