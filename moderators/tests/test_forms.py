import unittest

from django.utils import timezone
from django.test import TestCase
from django.forms import ValidationError

from nose.tools import *
from django_nose.tools import *

from .factories import UserFactory
from core.tests.factories import ThreadFactory, BoardFactory, PostFactory
from moderators.forms import ModActionForm

class ModActionFormTest(TestCase):
    def test_validation(self):
        t = ThreadFactory(board=BoardFactory())
        user = UserFactory()
        t.board.moderators.add(user)
        t.board.save()
        p = PostFactory(thread=t)

        # test form valid with a thread as content_object
        data = {'content_object': "t%s" % t.id,
                'action': 'delete', 'reason': 'Reason.'}
        form = ModActionForm(data=data, user=user)
        form.full_clean()
        ok_(form.is_valid())
        eq_(form.cleaned_data['moderator'], user)

        # test form valid with a post as content_object
        data = {'content_object': "%s" % p.pk,
                'action': 'delete', 'reason': 'Reason.'}
        form = ModActionForm(data=data, user=user)
        form.full_clean()
        ok_(form.is_valid())

        # testing required fields
        data = {}
        form = ModActionForm(data=data, user=user)
        ok_(not form.is_valid())
        assert_in('content_object', form.errors)
        assert_in('reason', form.errors)
        assert_in('action', form.errors)

        # testing that only moderators are allowed
        user2 = UserFactory()
        data = {'content_object': "t%s" % t.id,
                'action': 'delete', 'reason': 'Reason.'}
        form = ModActionForm(data=data, user=user2)
        ok_(not form.is_valid())
        assert_in('content_object', form.errors)

        # test `ban` action requires until field
        data = {'content_object': "t%s" % t.id,
                'action': 'ban', 'reason': 'Reason.'}
        form = ModActionForm(data=data, user=user)
        ok_(not form.is_valid())
        assert_in('__all__', form.errors)

        # test `ban` action requires IP field on content_object
        data = {'content_object': "t%s" % t.id, 'until': timezone.now(),
                'action': 'ban', 'reason': 'Reason.'}
        form = ModActionForm(data=data, user=user)
        ok_(not form.is_valid())
        assert_in('__all__', form.errors)
        assert_in('does not have IP field', form.errors['__all__'][0])

        # test `content_object` does not exist in the DB
        data = {'content_object': "t%s" % 123,
                'action': 'ban', 'reason': 'Reason.'}
        form = ModActionForm(data=data, user=user)
        ok_(not form.is_valid())
        assert_in('content_object', form.errors)

        # test only threads can be closed or pinned
        # testing with a post
        data = {'content_object': p.pk,
                'action': 'close', 'reason': 'Reason.'}
        form = ModActionForm(data=data, user=user)
        ok_(not form.is_valid())
        assert_in('__all__', form.errors)
        eq_('Only threads can be closed or pinned', form.errors['__all__'][0])
        # test with a thread
        data['content_object'] = "t%d" % t.pk
        form = ModActionForm(data=data, user=user)
        ok_(form.is_valid())
