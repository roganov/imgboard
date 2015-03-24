from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST

from .forms import ModActionForm

@require_POST
@login_required()
def moderator_view(request, slug):
    form = ModActionForm(request.POST, user=request.user)

    if form.is_valid():
        mod_action = form.save()
        if request.is_ajax():
            return JsonResponse({'status': 'ok', 'data': {'action': mod_action.action}})
        else:
            if mod_action.content_type.model == 'thread' and mod_action.action == 'delete':
                url = reverse('board', kwargs={'slug': slug})
            else:
                url = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(url)
    else:
        if request.is_ajax():
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        else:
            return HttpResponse("Error!", status=400)
