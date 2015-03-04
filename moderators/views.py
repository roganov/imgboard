from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from core.models import Board
from .forms import ModActionForm

@require_POST
@login_required()
def moderator_view(request, slug):
    form = ModActionForm(request.POST, user=request.user)

    if form.is_valid():
        mod_action = form.save()
        return JsonResponse({'status': 'ok', 'data': {'action': mod_action.action}})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
