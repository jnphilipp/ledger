# -*- coding: utf-8 -*-

import json

from categories.models import Tag
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone


@login_required
def autocomplete(request):
    """Handels GET/POST request to autocomplete tags.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == 'POST' else request.GET.copy()
    tags = Tag.objects.filter(entries__account__ledger__user=request.user).distinct()
    if 'q' in params:
        tags = tags.filter(name__icontains=params.pop('q')[0])
    data = {
        'response_date': timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
        'tags': [{
            'id': tag.id,
            'text': tag.name
        } for tag in tags]
    }
    return HttpResponse(json.dumps(data), 'application/json')
