from bisect import bisect_left
from functools import partial
import re
from itertools import chain


from django.core.urlresolvers import reverse

from .models import Thread, Post

def in_sorted(x, xs):
    i = bisect_left(xs, x)
    return i != len(xs) and xs[i] == x

def thread_id_url(t_ids, board):
    slug = board.slug

    existing_ts = Thread.objects.filter(id__in=t_ids, board=board)\
                        .order_by('id').values_list('id', flat=True)
    out = {}
    for t_id in t_ids:
        if in_sorted(t_id, existing_ts):  # thread id exists
            url = reverse('thread', kwargs={'thread_id': t_id, 'slug': slug})
            link = '<a class="reply" href={}>&gt;&gt;t{}</a>'.format(url, t_id)
        else:
            link = '&gt;&gt;t{}'.format(t_id)
        out[t_id] = link
    return out

def post_id_url(p_ids, board):
    slug = board.slug

    existing_p = Post.objects.filter(id__in=p_ids, thread__board=board).values_list('id', 'thread_id')
    existing_p_dict = dict(existing_p)

    out = {}

    for p_id in p_ids:
        try:
            thread_id = existing_p_dict[p_id]
            url = reverse('thread', kwargs={'thread_id': thread_id, 'slug': slug})
            link = '<a class="reply" href="{0}#{1}">&gt;&gt;{1}</a>'.format(url, p_id)
        except KeyError:
            link = '&gt;&gt;{}'.format(p_id)
        out[p_id] = link

    return out

# markup parsing escapes output, so `>` becomes `&gt;`
REG_REPLY = re.compile(r'\&gt;\&gt;(t?\d+)')
REG_SKIP = re.compile(r'(<code>.*?</code>|<pre>.*?</pre>)', re.I | re.S)
def sub_handle(m, t_ids, p_ids):
    reply_to = m.group(1)
    if reply_to[0] == 't':
        return t_ids[int(reply_to[1:])]
    else:
        return p_ids[int(reply_to)]

def replies_to_links(post_body, board):
    parts = REG_SKIP.split(post_body)
    texts, skip = parts[::2], parts[1::2]
    replies = chain.from_iterable(REG_REPLY.findall(text) for text in texts)
    thread_ids, post_ids = [], []
    for rep in replies:
        if rep[0] == 't':  # thread
            thread_ids.append(int(rep[1:]))
        else:  # post
            post_ids.append(int(rep))
    reply_to_post_urls = post_id_url(post_ids, board)
    reply_to_thread_urls = thread_id_url(thread_ids, board)

    sub_fun = partial(sub_handle, t_ids=reply_to_thread_urls, p_ids=reply_to_post_urls)
    texts_with_replies = (REG_REPLY.sub(sub_fun, text) for text in texts)

    return ''.join(merge(texts_with_replies, skip))

def merge(xs, ys):
    # TODO: make this function less ugly
    xs, ys = iter(xs), iter(ys)
    while 1:
        try:
            yield next(xs)
        except StopIteration:
            for y in ys:
                yield y
            break
        try:
            yield next(ys)
        except StopIteration:
            for x in xs:
                yield x
            break
