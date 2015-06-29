from accounts.models import Account, Tag
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from json import dumps

@login_required(login_url='/signin/')
def tags(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = {}
    data['xAxis'] = {'categories':[tag.name.lower() for tag in Tag.objects.filter(id__in=account.entry_set.values_list('tags', flat=True)).distinct()]}
    series = [{'name':'entries', 'data':[[tag.name.lower(), tag.count] for tag in Tag.objects.filter(id__in=account.entry_set.values_list('tags', flat=True)).extra(select={'count':'SELECT COUNT(*) FROM accounts_entry JOIN accounts_entry_tags ON accounts_entry.id=accounts_entry_tags.entry_id WHERE accounts_entry_tags.tag_id=accounts_tag.id AND accounts_entry.account_id=%s'}, select_params=(account.id,)).distinct()]}]
    data['series'] = series

    mimetype = 'application/json'
    return HttpResponse(dumps(data), mimetype)