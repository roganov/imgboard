from datetime import timedelta

from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone
from django_nose.tools import *
from nose.tools import *

from core.tests.factories import BoardFactory, ThreadFactory
from .factories import UserFactory
from ..models import ModeratorAction
from ..decorators import check_ban


class CheckBanTest(TestCase):

    def setUp(self):
        self.u = UserFactory()
        self.t = ThreadFactory(board=BoardFactory(), ip='77.47.204.159')
        self.factory = RequestFactory()

    def test_banned_user_cannot_post(self):
        until = timezone.now() + timedelta(days=1)
        self.ban_action = ModeratorAction.objects.create_ban(reason='reason',
                                                             moderator=self.u,
                                                             until=until,
                                                             content_object=self.t)
        check_ban_view = check_ban(lambda *a, **k: 'ok')
        r = self.factory.post('/', HTTP_X_FORWARDED_FOR='77.47.204.159')
        resp = check_ban_view(r)
        assert_code(resp, 403)
        eq_(resp['Content-Type'], 'text/html; charset=utf-8')

        r.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        resp = check_ban_view(r)
        assert_code(resp, 403)
        eq_(resp['Content-Type'], 'application/json')

    def test_expired_banned_can_post(self):
        until = timezone.now() - timedelta(days=1)
        self.ban_action = ModeratorAction.objects.create_ban(reason='reason',
                                                             moderator=self.u,
                                                             until=until,
                                                             content_object=self.t)
        check_ban_view = check_ban(lambda *a, **k: 'ok')
        r = self.factory.post('/', HTTP_X_FORWARDED_FOR='77.47.204.159')
        resp = check_ban_view(r)
        eq_(resp, 'ok')