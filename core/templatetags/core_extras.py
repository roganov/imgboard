from django import template

from ..models import Board

register = template.Library()

@register.assignment_tag
def get_boards():
    return list(Board.objects.order_by('pk'))
