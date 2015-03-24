import factory

from ..models import Board, Thread, Post


class PostFactory(factory.DjangoModelFactory):
    class Meta:
        model = Post

class ThreadFactory(factory.DjangoModelFactory):
    class Meta:
        model = Thread


class BoardFactory(factory.DjangoModelFactory):
    slug = factory.sequence(lambda n: 'test{}'.format(n))
    class Meta:
        model = Board


