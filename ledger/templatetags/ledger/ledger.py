# -*- coding: utf-8 -*-

from . import register
from accounts.models import Entry
from accounts.templatetags.accounts import colorfy
from datetime import date
from django.db.models import Sum
from ledger.functions.dates import get_last_date_current_month
from units.models import Unit


@register.inclusion_tag('ledger/partials/_balances.html', takes_context=True)
def balance(context, entries=None):
    values = []
    for unit in Unit.objects.filter(id__in=set(entries.values_list('account__unit', flat=True))):
        e = entries.filter(account__unit=unit)
        values.append({'balance': colorfy(e.filter(day__lte=date.today()).aggregate(sum=Sum('amount'))['sum'], unit), 'outstanding': colorfy(e.filter(day__gt=date.today()).filter(day__lte=get_last_date_current_month()).aggregate(sum=Sum('amount'))['sum'], unit)})
    return {'values':values}
