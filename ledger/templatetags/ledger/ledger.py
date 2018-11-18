# -*- coding: utf-8 -*-

from . import register
from accounts.models import Entry
from accounts.templatetags.accounts import colorfy
from datetime import date
from django.db.models import Sum
from django.utils import timezone
from ledger.functions.dates import get_last_date_current_month
from units.models import Unit


@register.inclusion_tag('ledger/partials/_balances.html', takes_context=True)
def balance(context, account=None):
    values = []

    if account:
        entries = account.entries.all()
    else:
        entries = Entry.objects.filter(account__ledger__user=context['user'])

    ids = set(entries.values_list('account__unit', flat=True))
    for unit in Unit.objects.filter(id__in=ids):
        e = entries.filter(account__unit=unit)
        b = e.filter(day__lte=date.today()).aggregate(sum=Sum('amount'))['sum']
        o = e.filter(day__gt=date.today()). \
            filter(day__lte=get_last_date_current_month()). \
            aggregate(sum=Sum('amount'))['sum']
        values.append({
            'balance': colorfy(b, unit),
            'outstanding': colorfy(o, unit)
        })
    return {'values': values}


@register.simple_tag
def timestamp(format_str):
    return timezone.now().strftime(format_str)
