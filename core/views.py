from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Board, Thread
from .forms import PostForm, ThreadForm

import markup
import post_markup


def board_view(request, slug, page=None):
    board = get_object_or_404(Board, slug=slug)
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES, board=board)
        if form.is_valid():
            thread = form.save()
            return HttpResponseRedirect(thread.get_absolute_url())
    else:
        form = ThreadForm()
    page_num = int(page or '1')
    page = Board.objects.threads_page(page_num, board)
    return render(request, 'board.html', {'board': board, 'page': page, 'form': form})


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


@csrf_exempt
@require_POST
def markup_view(request):
    text = request.POST.get('text', '')
    board = get_object_or_404(Board, slug=request.POST.get('board_slug'))
    return JsonResponse({'markup': post_markup.replies_to_links(markup.parse(text), board)})
