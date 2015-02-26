import os

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django_nose.tools import *
from nose.tools import *
import mock

from ..models import Post
from ..markup import parse
from .factories import BoardFactory, ThreadFactory


TEST_PHOTO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_photo.jpg')


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

    @override_settings(MEDIA_ROOT='/tmp')
    def test_post(self):
        b = BoardFactory()
        with open(TEST_PHOTO_PATH) as f:
            r = self.client.post(b.get_absolute_url(), {'raw_body': 'Body', 'image': f})
        t = b.thread_set.latest('id')  # fetch created thread
        assert_redirects(r, t.get_absolute_url())
        eq_(t.raw_body, 'Body')
        # test that raw_body is transformed
        eq_(t.body, parse('Body'))
        ok_(os.path.exists('/tmp/' + t.image.name))

        r = self.client.post(b.get_absolute_url(), {'raw_body': 'Body'})
        assert_code(r, 200)  # error because image is required

        r = self.client.post(reverse('board', kwargs={'slug': 'nonexisting'}))
        assert_code(r, 404)

class TestThreadView(TestCase):
    def test_get(self):
        thread = ThreadFactory(board=BoardFactory())

        with mock.patch('core.models.PostsQuerySet.present', return_value=[]) as m:
            r = self.client.get(thread.get_absolute_url())
            m.assert_called_with()
        eq_(thread, r.context['thread'])
        assert_ok(r)

    @override_settings(MEDIA_ROOT='/tmp')
    def test_post(self):
        thread = ThreadFactory(board=BoardFactory())
        eq_(thread.post_set.count(), 0)

        r = self.client.post(thread.get_absolute_url(), {'raw_body': 'Test body.'})
        assert_redirects(r, thread.get_absolute_url())
        eq_(Post.objects.filter(thread=thread).count(), 1)

        r = self.client.post(thread.get_absolute_url(), {})
        assert_ok(r)  # error, no redirection

        with open(TEST_PHOTO_PATH) as f:
            r = self.client.post(thread.get_absolute_url(), {'raw_body': 'Body', 'image': f})
        p = Post.objects.filter(thread=thread).latest('pk')
        ok_(os.path.exists('/tmp/' + p.image.name))
        assert_redirects(r, thread.get_absolute_url())
