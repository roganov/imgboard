import json
from django.core.urlresolvers import reverse
from django.test import TestCase

from nose.tools import *
from django_nose.tools import *
from core.models import Post, Thread

from core.tests.factories import BoardFactory, ThreadFactory, PostFactory
from .factories import UserFactory


class ModViewTest(TestCase):
    # Dunno if I need to test all the actions
    # since they've been tested in the model manager and the form.
    # For now I'll test the deletion (which is actually hiding).
    def test_delete(self):
        t = ThreadFactory(board=BoardFactory())
        p = PostFactory(thread=t)
        u1 = UserFactory()
        t.board.moderators.add(u1)
        t.board.save()
        u2 = UserFactory()

        data = {'action': 'delete',
                'reason': 'Obscene language',
                'content_object': p.pk}

        # testing with anonymous user
        url = reverse('api-moderator', args=(t.board.slug,))
        r = self.client.post(url, data)
        ok_(not Post.objects.get(pk=p.pk).is_hidden)
        # redirects
        assert_code(r, 302)

        # testing success
        self.client.login(username=u1.username, password='password')
        r = self.client.post(url, data)
        assert_code(r, 302)
        hidden_post = Post.objects.get(pk=p.pk)
        ok_(hidden_post.is_hidden)

        # testing with not valid content_object
        data['content_object'] = 123
        r = self.client.post(url, data)
        eq_(r['Content-Type'], 'text/html; charset=utf-8')
        assert_code(r, 400)

        r = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        eq_(r['Content-Type'], 'application/json')
        assert_code(r, 400)
        resp_text = json.loads(r.content)
        eq_(resp_text['status'], 'error')
        assert_in('content_object', resp_text['errors'])

    def test_delete_thread_redirects_to_board(self):
        t = ThreadFactory(board=BoardFactory())
        u1 = UserFactory()
        t.board.moderators.add(u1)
        t.board.save()

        data = {'action': 'delete',
                'reason': 'Obscene language',
                'content_object': 't{}'.format(t.pk)}
        self.client.login(username=u1.username, password='password')
        url = reverse('api-moderator', args=(t.board.slug,))
        ok_(not Thread.objects.get(pk=t.pk).is_hidden)
        r = self.client.post(url, data)
        ok_(Thread.objects.get(pk=t.pk).is_hidden)
        assert_redirects(r, reverse('board', kwargs={'slug': t.board.slug}))


class TestLoginLogoutViews(TestCase):
    def test(self):
        u = UserFactory()
        t = ThreadFactory(board=BoardFactory())
        t.board.moderators.add(u)
        t.board.save()

        r = self.client.get(t.get_absolute_url())
        assert_not_in('Moderate', r.content)

        self.client.post(reverse('login'), {'username': u.username, 'password': 'password'})
        r = self.client.get(t.get_absolute_url())
        assert_in('Moderate', r.content)
        assert_in('Logout', r.content)

        r = self.client.get(reverse('logout'))
        r = self.client.get(t.get_absolute_url())
        assert_not_in('Moderate', r.content)
