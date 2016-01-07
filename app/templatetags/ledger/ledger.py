# -*- coding: utf-8 -*-

from accounts.functions.dates import get_last_date_current_month
from accounts.models import Entry, Unit
from accounts.templatetags.accounts import colorfy
from app.templatetags.ledger import register
from datetime import date
from django.db.models import Sum

@register.inclusion_tag('ledger/partials/balances.html', takes_context=True)
def balance(context, user):
    values = []
    units = Unit.objects.filter(account__ledger__user=user).distinct()
    for unit in units:
        values.append({'balance':colorfy(Entry.objects.filter(account__ledger__user=user).filter(account__unit=unit).filter(day__lte=date.today()).aggregate(sum=Sum('amount'))['sum'], unit), 'outstanding':colorfy(Entry.objects.filter(account__ledger__user=user).filter(account__unit=unit).filter(day__gt=date.today()).filter(day__lte=get_last_date_current_month()).aggregate(sum=Sum('amount'))['sum'], unit)})
    return {'values':values}
