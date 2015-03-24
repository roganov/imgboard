from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, JsonResponse
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from moderators.decorators import check_ban
from .models import Board, Thread, Post
from .forms import PostForm, ThreadForm
from misc.recaptcha import captcha_every_n
from misc import markup
from . import post_markup
from moderators.forms import ModActionForm


@captcha_every_n
@check_ban
def board_view(request, slug, page=None):
    board = get_object_or_404(Board, slug=slug)
    if request.method == 'POST':
        with_captcha = request.session.get('posts_before_captcha', 0) == 0
        form = ThreadForm(request.POST, request.FILES,
                          board=board, request=request,
                          with_captcha=with_captcha)
        if form.is_valid():
            thread = form.save()
            response = HttpResponseRedirect(thread.get_absolute_url())
            return response
    else:
        form = ThreadForm()
    page_num = int(page or '1')
    page = Board.objects.threads_page(page_num, board)
    ctx = {'board': board, 'page': page,
           'form': form,
           'mod_form': ModActionForm(),
           'is_moderator': board.moderated_by(request.user)}
    return render(request, 'board.html', ctx)


@captcha_every_n
@check_ban
def thread_view(request, slug, thread_id):
    thread = get_object_or_404(Thread.objects.visible().select_related('board'), pk=thread_id)
    if request.method == 'POST':
        with_captcha = request.session.get('posts_before_captcha', 0) == 0
        form = PostForm(request.POST, request.FILES,
                        thread=thread, request=request,
                        with_captcha=with_captcha)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(thread.get_absolute_url())
    else:
        form = PostForm()
    posts = thread.post_set.present()
    ctx = {'board': thread.board, 'thread': thread,
           'form': form, 'posts': posts,
           'mod_form': ModActionForm(),
           'is_moderator': thread.board.moderated_by(request.user)}
    return render(request, 'thread.html', ctx)


@csrf_exempt
@require_POST
def markup_view(request):
    text = request.POST.get('text', '')
    board = get_object_or_404(Board, slug=request.POST.get('board_slug'))
    return JsonResponse({'markup': post_markup.replies_to_links(markup.parse(text), board)})

@csrf_exempt
@require_GET
def preview(request, slug, id_):
    if id_[0] == 't':
        prev = get_object_or_404(Thread, board__slug=slug, pk=id_[1:])
    else:
        prev = get_object_or_404(Post, thread__board__slug=slug, pk=id_)
    return render_to_response('_post.html', {'post': prev})

@csrf_exempt
@require_GET
def new_posts_view(request, slug, thread_id):
    latest_post_id = request.GET.get('latest_id')
    if latest_post_id is None or not latest_post_id.isdigit():
        latest_post_id = -1  # get all posts
    new_posts = Post.objects.new_posts(latest_id=latest_post_id,
                                       thread_id=thread_id,
                                       board_slug=slug)
    t = get_template('_post.html')
    posts = [t.render(Context({'post': post}))
             for post in new_posts]
    return JsonResponse({'posts': posts})
