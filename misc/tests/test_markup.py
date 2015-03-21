import unittest

from nose.tools import *
from ..markup import parse

class TestMarkup(unittest.TestCase):
    def test(self):
        eq_(parse('*Italic*'), '<p><i>Italic</i></p>')
        eq_(parse('**Bold**'), '<p><b>Bold</b></p>')
        eq_(parse('`>`'), '<p><code>&gt;</code></p>'),
        eq_(parse('~~Deleted~~'), '<p><del>Deleted</del></p>')
        eq_(parse('- Item1\n- Item2\n'), '<ul><li>Item1</li><li>Item2</li></ul>')
        eq_(parse('http://google.com'), "<p><a href=\'http://google.com\'>http://google.com</a></p>")
        eq_(parse('`inline`'), "<p><code>inline</code></p>")
        eq_(parse('*Italic* `inline`'), "<p><i>Italic</i> <code>inline</code></p>")
        eq_(parse('```\nprint \'foo\'\n```'), "<pre>print 'foo'</pre>")

