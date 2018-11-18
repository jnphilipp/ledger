# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from datetime import date
from django.db.models import Sum
from django.template import Library
from django.utils.numberformat import format
from django.utils.safestring import mark_safe
from ledger.functions.dates import get_last_date_current_month
from units.models import Unit


register = Library()


@register.filter
def floatdot(value, precision=2):
    if not value:
        return format(0, ',', precision)
    else:
        return format(round(value, precision), ',', precision)


@register.filter
def colorfy(amount, unit=None):
    if amount:
        color = 'green' if amount >= 0 else 'red'
        return mark_safe('<span class="%s">%s %s</span>' % (color,
                         floatdot(amount, unit.precision if unit else 2),
                         unit.symbol if unit else ''))
    else:
        return '%s %s'.strip() % (floatdot(0, unit.precision if unit else 2),
                                  unit.symbol if unit else '')


@register.filter
def balance(account):
    if account.closed:
        balance = 0
    else:
        balance = account.entries.filter(day__lte=date.today()). \
            aggregate(Sum('amount'))['amount__sum']
    return colorfy(balance, account.unit)


@register.filter
def outstanding(account):
    if account.closed:
        outstanding = 0
    else:
        outstanding = account.entries.filter(day__gt=date.today()). \
            filter(day__lte=get_last_date_current_month()). \
            aggregate(Sum('amount'))['amount__sum']
    return colorfy(outstanding, account.unit)


@register.inclusion_tag('accounts/partials/_balances.html', takes_context=True)
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
