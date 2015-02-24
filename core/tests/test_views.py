from django.test import TestCase
from django.core.urlresolvers import reverse

from django_nose.tools import *
from nose.tools import *
import mock

from ..models import Post
from .test_models import BoardFactory, ThreadFactory, PostFactory

class TestBoardView(TestCase):
    def test_get(self):
        b = BoardFactory(slug='test')
        r = self.client.get(reverse('board', kwargs={'slug': 'test'}))
        assert_ok(r)
        assert_template_used(r, 'board.html')

        r = self.client.get(reverse('board', kwargs={'slug': 'nonexistent'}))
        assert_code(r, 404)

        url = b.get_absolute_url()
        r = self.client.get(url)
        assert_ok(r)
        assert_template_used(r, 'board.html')
        assert_in('page', r.context)

class TestThreadView(TestCase):
    def test_get(self):
        thread = ThreadFactory(board=BoardFactory())

        with mock.patch('core.models.PostsQuerySet.present', return_value=[]) as m:
            r = self.client.get(thread.get_absolute_url())
            m.assert_called_with()
        eq_(thread, r.context['thread'])
        assert_ok(r)

    def test_post(self):
        thread = ThreadFactory(board=BoardFactory())
        eq_(thread.post_set.count(), 0)

        r = self.client.post(thread.get_absolute_url(), {'raw_body': 'Test body.'})
        assert_redirects(r, thread.get_absolute_url())
        eq_(Post.objects.filter(thread=thread).count(), 1)