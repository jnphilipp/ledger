# -*- coding: utf-8 -*-

import json

from categories.models import Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone


@login_required
def autocomplete(request):
    """Handels GET/POST request to autocomplete tags.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == 'POST' \
        else request.GET.copy()
    if 'application/json' == request.META.get('CONTENT_TYPE'):
        params.update(json.loads(request.body.decode('utf-8')))

    tags = Tag.objects.filter(
        entries__account__ledger__user=request.user).distinct(). \
        annotate(Count('entries')).order_by('-entries__count')
    q = []
    if 'q' in params:
        q = params.pop('q')[0]
        tags = tags.filter(name__icontains=q)
        q = [{'id': q, 'text': q}]

    data = {
        'response_date': timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
        'tags': q + [{
            'id': tag.id,
            'text': tag.name
        } for tag in tags]
    }
    return JsonResponse(data)
