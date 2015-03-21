from django import template

from misc import markup

register = template.Library()


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

