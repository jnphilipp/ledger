# -*- coding: utf-8 -*-

from accounts.models import Account
from categories.models import Category
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _


@login_required
def categories(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = {
        'xAxis': {
            'categories': [c.name for c in Category.objects.filter(
                id__in=account.entries.values_list('category',
                                                   flat=True)).distinct()],
            'title': {
                'text': str(_('Categories'))
            }
        },
        'yAxis': {
            'title': {
                'text': str(_('Number of times used'))
            }
        },
        'series': [{
            'name': 'entries',
            'data': [[c.name, c.count] for c in Category.objects.filter(id__in=account.entries.values_list('category', flat=True)).extra(select={'count':'SELECT COUNT(*) FROM accounts_entry WHERE accounts_entry.category_id=categories_category.id AND accounts_entry.account_id=%s'}, select_params=(account.id,)).distinct()]
        }]
    }
    return JsonResponse(data)

