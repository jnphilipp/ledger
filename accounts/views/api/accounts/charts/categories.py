from accounts.models import Account, Category
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from json import dumps

@login_required(login_url='/signin/')
def categories(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = {}
    data['xAxis'] = {'categories':[category.name.lower() for category in Category.objects.filter(id__in=account.entry_set.values_list('category', flat=True)).distinct()]}
    series = [{'name':'entries', 'data':[[category.name.lower(), category.count] for category in Category.objects.filter(id__in=account.entry_set.values_list('category', flat=True)).extra(select={'count':'SELECT COUNT(*) FROM accounts_entry WHERE accounts_entry.category_id=accounts_category.id AND accounts_entry.account_id=%s'}, select_params=(account.id,)).distinct()]}]
    data['series'] = series

    mimetype = 'application/json'
    return HttpResponse(dumps(data), mimetype)