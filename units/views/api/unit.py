# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from json import dumps
from units.models import Unit


@login_required(login_url='/users/signin/')
def autocomplete(request):
    """Handels GET/POST request to autocomplete units.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == 'POST' else request.GET.copy()
    units = Unit.objects.filter(accounts__ledger__user=request.user).distinct()
    if 'q' in params:
        units = units.filter(name__icontains=params.pop('q')[0])
    data = {'response_date':timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
            'units': [{'id':unit.id, 'text':unit.name.lower()} for unit in units]}
    return HttpResponse(dumps(data), 'application/json')
