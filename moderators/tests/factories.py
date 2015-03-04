import factory
from django.contrib.auth import get_user_model

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'username%d' % n)
    password = 'password'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.objects.create_user(*args, **kwargs)