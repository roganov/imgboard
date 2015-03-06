import json
from django.core.urlresolvers import reverse
from django.test import TestCase

from nose.tools import *
from django_nose.tools import *
from core.models import Post

from core.tests.factories import BoardFactory, ThreadFactory, PostFactory
from .factories import UserFactory


class ModViewTest(TestCase):
    # Dunno if I need to test all the actions
    # since they've been tested in the model manager and the form.
    # For now I'll test the deletion (actually hiding).
    def test_delete(self):
        t = ThreadFactory(board=BoardFactory())
        p = PostFactory(thread=t)
        u = UserFactory()
        t.board.moderators.add(u)
        t.board.save()

        data = {'action': 'delete',
                'reason': 'Obscene language',
                'content_object': p.pk}

        # testing with anonymous user
        url = reverse('api-moderator', args=(t.board.slug,))
        r = self.client.post(url, data)
        # redirects
        assert_code(r, 302)

        # testing success
        self.client.login(username=u.username, password='password')
        r = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        resp_text = json.loads(r.content)
        assert_ok(r)
        eq_(resp_text['status'], 'ok')
        hidden_post = Post.objects.get(pk=p.pk)
        ok_(hidden_post.is_hidden)

        # testing with not valid content_object
        data['content_object'] = 123
        r = self.client.post(url, data)
        resp_text = json.loads(r.content)
        assert_code(r, 400)
        eq_(resp_text['status'], 'error')
        assert_in('content_object', resp_text['errors'])
