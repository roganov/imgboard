from django.test import TestCase
from django.forms.models import model_to_dict

import factory
import time

from .models import Board, Thread, Post

class PostFactory(factory.DjangoModelFactory):
    class Meta:
        model = Post

class ThreadFactory(factory.DjangoModelFactory):
    class Meta:
        model = Thread


class BoardFactory(factory.DjangoModelFactory):
    class Meta:
        model = Board

class TestThread(TestCase):
    def test_visible(self):
        b = BoardFactory()
        ThreadFactory(board=b, is_hidden=True)
        ThreadFactory.create_batch(size=3, board=b)
        self.assertEqual(b.thread_set.count(), 4)
        self.assertEqual(b.thread_set.visible().count(), 3)

    def test_order(self):
        b = BoardFactory()
        t1 = ThreadFactory(board=b)
        t2 = ThreadFactory(board=b, is_pinned=True)
        t3 = ThreadFactory(board=b)
        self.assertEqual(list(Thread.objects.order()), [t2, t3, t1])

    def test_create(self):
        board = BoardFactory()
        thread = ThreadFactory(board=board)
        self.assertTrue(thread.pk)

    def test_create_hides_the_oldest_thread(self):
        board = BoardFactory(threads_per_page=2, pages_num=2)
        thread_ids = []
        for _ in range(board.threads_per_page * board.pages_num + 1):
            thread = ThreadFactory(board=board)
            thread_ids.append(thread.pk)
        threads = [Thread.objects.get(pk=pk) for pk in thread_ids]
        self.assertTrue(threads[0].is_hidden)
        self.assertTrue(all(not t.is_hidden for t in threads[1:]))


class TestPost(TestCase):
    def test_create_bumps_post_increments_count(self):
        b = BoardFactory()
        t = ThreadFactory(board=b)
        old_bumped = t.bumped_at
        time.sleep(0.1)
        p = PostFactory(thread=t)
        new_t = Thread.objects.get(pk=t.pk)
        self.assertLess(old_bumped, new_t.bumped_at)
        self.assertEqual(p.created_at, new_t.bumped_at)
        self.assertEqual(new_t.posts_count, 1)
        PostFactory(thread=t)
        t = Thread.objects.get(pk=t.pk)
        self.assertEqual(t.posts_count, 2)
        self.assertEqual(t.posts_count, t.post_set.count())
