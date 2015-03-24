from cgi import escape

from nose.tools import *
from django.test import TestCase
from django.test.utils import override_settings

from core.post_markup import thread_id_url, post_id_url, replies_to_links
from .factories import PostFactory, ThreadFactory, BoardFactory


class TestRepliesToLinks(TestCase):
    def test_thread_id_url(self):
        t = ThreadFactory(board=BoardFactory())
        res = thread_id_url([t.id, 10], t.board)
        ok_(res[t.id].startswith('<a class="reply"'))
        eq_(res[10], "&gt;&gt;t10")

    def test_post_id_url(self):
        t = ThreadFactory(board=BoardFactory())
        p = PostFactory(thread=t)
        res = post_id_url([p.id, 10], t.board)
        ok_(res[p.id].startswith('<a class="reply"'))
        eq_(res[10], "&gt;&gt;10")

    def test_replies_to_link(self):
        t = ThreadFactory(board=BoardFactory())
        with_reps = replies_to_links(escape('>>t1'), t.board)
        ok_(with_reps.startswith('<a class="reply"'))
        assert_in(t.get_absolute_url(), with_reps)

        in_code = "<code>{}</code>".format(escape('>>t1'))
        eq_(replies_to_links(in_code, t.board), in_code)



@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
})
class TestCacheBoardView(TestCase):
    def test(self):
        thread = ThreadFactory(board=BoardFactory())

        # cold cache
        with self.assertNumQueries(5):
            self.client.get(thread.board.get_absolute_url())

        # warm cache
        with self.assertNumQueries(0):
            self.client.get(thread.board.get_absolute_url())

        PostFactory(thread=thread)

        # new post invalidated old cache
        # not 5 as before because one query is cached in template fragment
        with self.assertNumQueries(4):
            self.client.get(thread.board.get_absolute_url())

    def test_new_thread_purges_cache(self):
        thread1 = ThreadFactory(board=BoardFactory(), title='Thread1')
        r = self.client.get(thread1.board.get_absolute_url())
        assert_in('Thread1', r.content)

        thread2 = ThreadFactory(board=thread1.board, title='Thread2')
        r = self.client.get(thread1.board.get_absolute_url())
        assert_in('Thread1', r.content)
        assert_in('Thread2', r.content)