import os
import time

from django.test import TestCase
from django.core.files.base import File
from django.test.utils import override_settings

from ..models import Board, Thread, Post
from .factories import BoardFactory, ThreadFactory, PostFactory
from .test_views import TEST_PHOTO_PATH


class TestBoard(TestCase):
    def test_board_paginator(self):
        b = BoardFactory(threads_per_page=2, pages_num=2)
        ts = ThreadFactory.create_batch(size=4, board=b)
        for t in ts:
            PostFactory(thread=t)
        threads_page = Board.objects.threads_page(page_num=2, board=b).object_list
        # assert that threads are sorted in reverse order
        self.assertEqual(list(threads_page), [ts[1], ts[0]])

        PostFactory.create_batch(size=10, thread=ts[1])
        PostFactory.create_batch(size=2, thread=ts[0])
        threads_page = Board.objects.threads_page(page_num=1, board=b).object_list
        # assert sorting
        self.assertEqual(threads_page, [ts[0], ts[1]])
        # assert that posts are fetched
        self.assertEqual(len(threads_page[0].latest_posts), 3)
        # assert that only 4 posts are fetched (10 total)
        self.assertEqual(len(threads_page[1].latest_posts), 4)
        # assert that attached posts are sorted in ascending order
        posts = threads_page[1].latest_posts
        self.assertTrue(all(p.created_at < pp.created_at for p, pp in zip(posts, posts[1:])))


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
        self.assertEqual(list(b.thread_set.order()), [t2, t3, t1])

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

    @override_settings(MEDIA_ROOT='/tmp/')
    def test_save_creates_thumbnail(self):
        board=BoardFactory()
        with open(TEST_PHOTO_PATH) as f:
            img = File(f)
            thread = Thread(board=board, image=img)
            self.assertFalse(thread.thumbnail)
            thread.save()
        self.assertTrue(thread.thumbnail)
        self.assertTrue(os.path.exists("/tmp/" + thread.image.name))
        name = thread.image.name.split("/")[-1]
        self.assertTrue(os.path.exists("/tmp/thumbs/" + name))


class TestPost(TestCase):
    def test_create_bumps_post_and_increments_count(self):
        b = BoardFactory()
        t = ThreadFactory(board=b)
        old_bumped = t.bumped_at
        time.sleep(0.1)
        p = PostFactory(thread=t)
        new_t = Thread.objects.get(pk=t.pk)
        self.assertLess(old_bumped, new_t.bumped_at)
        self.assertEqual(p.created_at, new_t.bumped_at)
        self.assertEqual(new_t.posts_count, 1)
        p = PostFactory(thread=t)
        t = Thread.objects.get(pk=t.pk)
        self.assertEqual(p.created_at, t.bumped_at)
        self.assertEqual(t.posts_count, 2)
        self.assertEqual(t.posts_count, t.post_set.count())

    def test_new_posts(self):
        t = ThreadFactory(board=BoardFactory())
        posts = PostFactory.create_batch(size=5, thread=t)
        PostFactory(thread=t, is_hidden=True)
        new_posts = Post.objects.new_posts(posts[0].id, thread_id=t.id,
                                           board_slug=t.board.slug)
        self.assertEqual(len(new_posts), 4)

        t2 = ThreadFactory(board=BoardFactory())
        new_posts = Post.objects.new_posts(posts[0].id, thread_id=t2.id,
                                           board_slug=t.board.slug)
        self.assertEqual(len(new_posts), 0)

    def test_present(self):
        t = ThreadFactory(board=BoardFactory())
        ps = PostFactory.create_batch(size=5, thread=t)
        PostFactory(is_hidden=True, thread=t)
        # test hidden is not visible
        self.assertEqual(t.post_set.present().count(), 5)
        # test correct order
        self.assertEqual(list(t.post_set.present().all()), ps)