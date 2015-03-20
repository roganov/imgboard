from collections import defaultdict
from json import dumps
from redis import StrictRedis
from werkzeug.wrappers import Request, Response

from gevent import spawn, monkey
monkey.patch_all()
from gevent.queue import Queue
from gevent.pywsgi import WSGIServer

class Registry(object):
    def __init__(self):
        self.channels = defaultdict(set)

    def _get_channel(self, board_slug, thread_id):
        return '{}.{}'.format(board_slug, thread_id)

    def sub(self, board_slug, thread_id, buffer):
        channel = self._get_channel(board_slug, thread_id)
        self.channels[channel].add(buffer)

    def unsub(self, board_slug, thread_id, buffer):
        channel = self._get_channel(board_slug, thread_id)
        self.channels[channel].remove(buffer)

    def pub(self, board_slug, thread_id, message):
        print self.channels
        channel = self._get_channel(board_slug, thread_id)
        data = message['data']
        for buf in self.channels[channel]:
            buf.put_nowait(data)

registry = Registry()

def listener():
    rs = StrictRedis()
    p = rs.pubsub()
    p.psubscribe('boards.*')
    for message in p.listen():
        print message
        if message['type'] != 'pmessage':
            continue
        _, board_slug, thread_id = message['channel'].split('.')
        registry.pub(board_slug, thread_id, message)

class Stream(object):
    def __init__(self, board_slug, thread_id):
        print 'NEW CONN'
        self.q = Queue()
        self.board_slug = board_slug
        self.thread_id = thread_id
        registry.sub(board_slug, thread_id, self.q)

    def __iter__(self):
        yield dumps({'type': 'connected'})
        for post in self.q:
            payload = {'type': 'new-posts', 'posts': [post]}
            yield dumps(payload)

    def close(self):
        print 'DISCONNECT'
        registry.unsub(self.board_slug, self.thread_id, self.q)


def application(environ, start_response):
    request = Request(environ)
    board_slug = request.args.get('board_slug')
    thread_id = request.args.get('thread_id')
    if not board_slug or not thread_id:
        body = '{"type": "error"}'
        response = Response(body, mimetype='application/json', status=404)
    else:
        body = Stream(board_slug, thread_id)
        response = Response(body, mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response(environ, start_response)

spawn(listener)
WSGIServer(('', 8001), application).serve_forever()