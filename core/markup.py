import re
from cgi import escape
from itertools import groupby, takewhile
from operator import attrgetter
from itertools import imap

from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight as pyg_highlight
from pygments.util import ClassNotFound


REG_TOP_LEVEL = re.compile(r'''(?imx)
    (?P<quote> \s*> \ )
   |(?P<code>  \ {4}|\t)
   |(?P<fence> ```)
   |(?P<ul> [-*]\ )
   |(?P<br> \s*$)
   # catch-all
   |(?P<p> \s*)
''')

block_functions = {
    'quote': lambda ys: u"<blockquote>{}</blockquote>".format(parse_span_level(' '.join(ys))),
    'p':     lambda ys: u"<p>{}</p>".format(parse_span_level(' '.join(ys))),
    'code':  lambda ys: highlight('\n'.join(ys)),
    'fence': lambda code, lang: highlight(code, lang),
    'ul':    lambda ys: u"<ul><li>{}</li></ul>".format("</li><li>".join(parse_span_level(y) for y in ys)),
    'br':    lambda _: ''
}
def parse_block_level(xs):
    groups = groupby(imap(REG_TOP_LEVEL.match, xs), key=attrgetter('lastgroup'))
    for gname, matches in groups:
        ys = (m.string[m.end():] for m in matches)
        if gname == 'fence':
            lang = next(ys)
            code = "\n".join(takewhile(lambda l: not l.startswith('```'), xs))
            yield block_functions[gname](code, lang)
        else:
            yield block_functions[gname](ys)

REG_LINE_LEVEL = re.compile(r'''(?imx)
    (?P<b> \*\* (?P<_b>.+?) \*\*)
   |(?P<i> \* (?P<_i>.+?) \*)
   |(?P<strike> ~~ (?P<_strike>.+?) ~~)
   |(?P<spoiler> %% (?P<_spoiler>.+?) %%)
   |(?P<code> \` (?P<_code>.+?) \`)
   # the URL regex is stolen from http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
   # it may as well be faulty
   |(?P<url> http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+ )
   |(?P<text> .+?)
''')

span_functions = {
    'code':    lambda m: u"<code>{}</code>".format(escape(m.group('_code'))),
    'url':     lambda m: u"<a href='{0}'>{0}</a>".format(m.group()),
    'b':       lambda m: u"<b>{}</b>".format(parse_span_level(m.group('_b'))),
    'i':       lambda m: u"<i>{}</i>".format(parse_span_level(m.group('_i'))),
    'strike':  lambda m: u"<del>{}</del>".format(parse_span_level(m.group('_strike'))),
    'spoiler': lambda m: u"<span class='spoiler'>{}</span>".format(parse_span_level(m.group('_spoiler'))),
    'text':    lambda m: escape(m.group('text')),
}

def parse_span_level(line):
    return REG_LINE_LEVEL.sub(lambda m: span_functions[m.lastgroup](m), line)

def highlight(code, lang=None, formatter=HtmlFormatter()):
    try:
        lexer = get_lexer_by_name(lang)
        return pyg_highlight(code, lexer, formatter)
    except ClassNotFound:
        return u"<pre>{}</pre>".format(escape(code))

def parse(input):
    return u"\n".join(parse_block_level(iter(input.splitlines())))