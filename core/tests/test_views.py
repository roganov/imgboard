import json
import os
from urllib import urlencode

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django_nose.tools import *
from nose.tools import *
import mock

from ..models import Post
from ..markup import parse
from .factories import BoardFactory, ThreadFactory, PostFactory


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

        # posting with image
        with open(TEST_PHOTO_PATH) as f:
            r = self.client.post(b.get_absolute_url(), {'raw_body': 'Body', 'image': f})
        t = b.thread_set.latest('id')  # fetch created thread
        assert_redirects(r, t.get_absolute_url())
        eq_(t.raw_body, 'Body')
        # test that raw_body is transformed
        eq_(t.body, parse('Body'))
        ok_(os.path.exists('/tmp/' + t.image.name))

        # image is required, thread creation must fail
        r = self.client.post(b.get_absolute_url(), {'raw_body': 'Body'})
        assert_code(r, 200)
        ok_(r.context['form'].errors['image'])

        # raw_boy must include visible characters, thread creation must fail
        r = self.client.post(b.get_absolute_url(), {'raw_body': '   \n  \t   '})
        assert_code(r, 200)
        ok_(r.context['form'].errors['raw_body'])

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

    def test_cannot_view_hidden_thread(self):
        thread = ThreadFactory(board=BoardFactory())
        r = self.client.get(thread.get_absolute_url())
        assert_ok(r)
        thread.is_hidden = True
        thread.save()
        r = self.client.get(thread.get_absolute_url())
        assert_code(r, 404)


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

class TestPreview(TestCase):
    def test(self):
        t = ThreadFactory(board=BoardFactory())
        r = self.client.get(reverse('api-preview', args=(t.board.slug, "t{}".format(t.pk))))
        assert_ok(r)
        assert_template_used(r, '_post.html')

        r = self.client.get(reverse('api-preview', args=(t.board.slug, "t{}".format(t.pk + 1))))
        assert_code(r, 404)

        p = PostFactory(thread=t)
        r = self.client.get(reverse('api-preview', args=(t.board.slug, p.pk)))
        assert_ok(r)

class TestNewPosts(TestCase):
    def test(self):
        t = ThreadFactory(board=BoardFactory())
        PostFactory.create_batch(size=2, thread=t)
        url = reverse('api-new-posts', kwargs={'thread_id': t.id, 'slug': t.board.slug})
        url = '{}?{}'.format(url, urlencode({'latest_id': 1}))
        r = self.client.get(url)
        assert_ok(r)
        assert_template_used(r, '_post.html')
        posts = json.loads(r.content)
        eq_(len(posts), 1)
