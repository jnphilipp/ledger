# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from datetime import date
from django.db.models import Sum
from django.template import Library
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe
from ledger.dates import get_last_date_current_month
from units.models import Unit


register = Library()


@register.filter
def colorfy(amount, unit=None):
    precision = unit.precision if unit else 2
    symbol = unit.symbol if unit else ''
    if amount:
        return mark_safe(f'<span class="{"green" if amount >= 0 else "red"}"' +
                         f'>{floatformat(amount, precision)} {symbol}</span>')
    else:
        return f'{floatformat(0, precision)} {symbol}'.strip()


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
        balance = e.filter(day__lte=date.today()). \
            aggregate(sum=Sum('amount'))['sum']
        outstanding = e.filter(day__gt=date.today()). \
            filter(day__lte=get_last_date_current_month()). \
            aggregate(sum=Sum('amount'))['sum']

        if account:
            values.append({
                'balance': colorfy(balance, unit),
                'outstanding': colorfy(outstanding, unit)
            })
        else:
            accounts = []
            for a in unit.accounts.filter(closed=False). \
                    filter(ledger__user=context['user']):
                b = a.entries.filter(day__lte=date.today()). \
                    aggregate(sum=Sum('amount'))['sum']
                o = a.entries.filter(day__gt=date.today()). \
                    filter(day__lte=get_last_date_current_month()). \
                    aggregate(sum=Sum('amount'))['sum']
                accounts.append({
                    'name': a.name,
                    'balance': '%s %s' % (floatdot(b, unit.precision),
                                          unit.symbol),
                    'outstanding': '%s %s' % (floatdot(o, unit.precision),
                                              unit.symbol)
                })

            values.append({
                'balance': colorfy(balance, unit),
                'outstanding': colorfy(outstanding, unit),
                'accounts': accounts
            })
    return {'values': values}
