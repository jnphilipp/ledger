# -*- coding: utf-8 -*-

from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from json import dumps


@login_required
def autocomplete(request):
    """Handels GET/POST request to autocomplete accounts.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == 'POST' else request.GET.copy()
    accounts = Account.objects.filter(ledger__user=request.user).distinct()
    if 'q' in params:
        accounts = accounts.filter(name__icontains=params.pop('q')[0])
    data = {'response_date':timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
            'accounts': [{'id':account.id, 'text':account.name.lower()} for account in accounts]}
    return HttpResponse(dumps(data), 'application/json')
