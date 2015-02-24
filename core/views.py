from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Board, Thread, Post
from .forms import PostForm

from django.views.generic import View
# Create your views here.

class BoardView(View):
    def get(self, *args, **kwargs):
        board = get_object_or_404(Board, slug=kwargs['slug'])
        page_num = int(kwargs.get('page') or '1')
        page = Board.objects.threads_page(page_num, board)
        return render(self.request, 'board.html', {'board': board, 'page': page})

def thread_view(request, slug, thread_id):
    thread = get_object_or_404(Thread.objects.select_related('board'), pk=thread_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, thread=thread)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(thread.get_absolute_url())
    else:
        form = PostForm()
    posts = thread.post_set.present()
    return render(request, 'thread.html', {'board': thread.board, 'thread': thread,
                                           'form': form, 'posts': posts})