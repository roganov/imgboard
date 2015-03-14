from mock import patch

from django.utils import timezone
from django.test import TestCase

from nose.tools import *
from django_nose.tools import *

from core.tests.factories import PostFactory, ThreadFactory, BoardFactory
from core.models import Thread
from ..models import Ban, ModeratorAction, ModeratorActionManager
from .factories import UserFactory


class ModActManagerTest(TestCase):
    def setUp(self):
        self.b = BoardFactory()
        self.t = ThreadFactory(board=self.b)
        self.p = PostFactory(thread=self.t)
        self.u = UserFactory()
        self.b.moderators.add(self.u)
        self.b.save()

    def test_dispatcher(self):
        with patch.object(ModeratorAction.objects, 'create_close') as m:
            ModeratorAction.objects.create_action(action='close')
        m.assert_called_with(action='close')


    def test_create_close(self):
        opts = {'content_object': self.t,
                'reason': 'Reason',
                'moderator': self.u}
        ok_(not self.t.is_closed)
        mod_action = ModeratorAction.objects.create_close(**opts)

        obj = Thread.objects.get(pk=self.t.pk)
        ok_(obj.is_closed)

    def test_create_pin(self):
        opts = {'content_object': self.t,
                'reason': 'Reason',
                'moderator': self.u}
        ok_(not self.t.is_pinned)
        mod_action = ModeratorAction.objects.create_pin(**opts)

        obj = Thread.objects.get(pk=self.t.pk)
        ok_(obj.is_pinned)

    def test_create_delete(self):
        opts = {'content_object': self.t,
                'reason': 'Reason',
                'moderator': self.u}
        ok_(not self.t.is_hidden)
        mod_action = ModeratorAction.objects.create_delete(**opts)

        obj = Thread.objects.get(pk=self.t.pk)
        ok_(obj.is_hidden)

    def test_create_delete_decrements_posts_count(self):
        opts = {'content_object': self.p,
                'reason': 'Reason',
                'moderator': self.u}
        t = Thread.objects.get(pk=self.t.pk)
        eq_(t.posts_count, 1)
        mod_action = ModeratorAction.objects.create_delete(**opts)
        updated_t = Thread.objects.get(pk=self.t.pk)
        eq_(updated_t.posts_count, 0)

    def test_create_delete_img(self):
        opts = {'content_object': self.t,
                'reason': 'Reason',
                'moderator': self.u}
        ok_(not self.t.is_hidden)
        mod_action = ModeratorAction.objects.create_delete_img(**opts)

        obj = Thread.objects.get(pk=self.t.pk)
        eq_(obj.image, '')
        eq_(obj.thumbnail, '')

    def test_create_ban(self):
        self.t = ThreadFactory(board=self.b, ip='127.0.0.1')
        opts = {'content_object': self.t,
                'reason': 'Reason',
                'moderator': self.u,
                'until': timezone.now()}
        ok_(not self.t.is_hidden)
        mod_action = ModeratorAction.objects.create_ban(**opts)

        ban = Ban.objects.latest('pk')
        eq_(ban.action, mod_action)
