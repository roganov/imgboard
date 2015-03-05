from functools import wraps

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, render_to_response

from .models import Ban
from ipware.ip import get_real_ip


def check_ban(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            try:
                ban = Ban.objects.select_related('action').get(until__gt=timezone.now(),
                                                               ip=get_real_ip(request))
                if request.is_ajax():
                    to_json = {'status': 'error', 'ban': {'created_at': ban.action.created_at,
                                                          'until': ban.until,
                                                          'reason': ban.action.reason}}
                    return JsonResponse(to_json, status=403)
                else:
                    resp = render_to_response('banned.html', {'ban': ban})
                    resp.status_code = 403
                    return resp
            except Ban.DoesNotExist:
                pass

        return f(request, *args, **kwargs)

    return wrapper