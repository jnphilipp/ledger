# -*- coding: utf-8 -*-

from accounts.models import Account
from categories.models import Tag
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _


@login_required
def tags(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = {
        'xAxis': {
            'categories': [t.name for t in Tag.objects.filter(
                id__in=account.entries.values_list('tags',
                                                   flat=True)).distinct()],
            'title': {
                'text': str(_('Tags'))
            }
        },
        'yAxis': {
            'title': {
                'text': str(_('Number of times used'))
            }
        },
        'series': [{
            'name': 'entries',
            'data': [[t.name, t.count] for t in Tag.objects.filter(id__in=account.entries.values_list('tags', flat=True)).extra(select={'count':'SELECT COUNT(*) FROM accounts_entry JOIN accounts_entry_tags ON accounts_entry.id=accounts_entry_tags.entry_id WHERE accounts_entry_tags.tag_id=categories_tag.id AND accounts_entry.account_id=%s'}, select_params=(account.id,)).distinct()]
        }]
    }
    return JsonResponse(data)
