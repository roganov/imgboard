from django import template

from ..models import Board

from .. import markup

register = template.Library()

@register.assignment_tag
def get_boards():
    return list(Board.objects.order_by('pk'))


class MarkupNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context).strip()
        return markup.parse(output)

@register.tag('markup')
def do_markup(parser, token):
    nodelist = parser.parse(('endmarkup', ))
    parser.delete_first_token()
    return MarkupNode(nodelist)

