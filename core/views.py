from django.shortcuts import render, get_object_or_404, render_to_response
from .models import Board, Thread, Post

from django.views.generic import View
# Create your views here.

class BoardView(View):
    def get(self, *args, **kwargs):
        board = get_object_or_404(Board, slug=kwargs['slug'])
        page_num = int(kwargs.get('page') or '1')
        page = Board.objects.threads_page(page_num, board)
        return render_to_response('board.html', {'board': board, 'page': page})

class ThreadView(View):
    def get(self, *args, **kwargs):
        thread = get_object_or_404(Thread.objects.select_related('board'), pk=kwargs['thread_id'])
        thread.post_set = thread.post_set.present()
        return render_to_response('thread.html', {'board': thread.board, 'thread': thread})
