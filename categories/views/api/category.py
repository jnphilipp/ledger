# -*- coding: utf-8 -*-

from categories.models import Category
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from json import dumps


@login_required
def autocomplete(request):
    """Handels GET/POST request to autocomplete categories.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == 'POST' else request.GET.copy()
    categories = Category.objects.filter(Q(entries__account__ledger__user=request.user) | Q(accounts__ledger__user=request.user)).distinct()
    if 'q' in params:
        categories = categories.filter(name__icontains=params.pop('q')[0])
    data = {
        'response_date':timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
        'categories': [{
            'id':category.id,
            'text':category.name.lower()
        } for category in categories]
    }
    return HttpResponse(dumps(data), 'application/json')
