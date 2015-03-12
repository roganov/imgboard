from django.test import TestCase, RequestFactory

from nose.tools import *
from django_nose.tools import *
from . import factories as f
from ..forms import PostForm


class TestPostForm(TestCase):
    def test_post_to_closed_thread_not_valid(self):
        t = f.ThreadFactory(board=f.BoardFactory(), is_closed=True)
        form = PostForm({'raw_body': 'Body'}, thread=t, request=RequestFactory().get('/'))
        ok_(not form.is_valid())
        eq_(form.errors.as_data()['__all__'][0].code, 'closed')
