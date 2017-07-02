# -*- coding: utf-8 -*-

from accounts.models import Account
from categories.models import Category, Tag
from datetime import date
from django.db.models import Q, Sum
from django.template import Library
from django.utils.numberformat import format
from django.utils.safestring import mark_safe
from ledger.functions.dates import get_last_date_current_month

register = Library()


@register.filter(is_safe=True)
def floatdot(value, precision=2):
    return format(0, ',', precision) if not value else format(round(value, precision), ',', precision)


@register.filter
def colorfy(amount, unit=None):
    return mark_safe('<span class="%s">%s %s</span>' % ('green' if amount >= 0 else 'red', floatdot(amount, unit.precision if unit else 2), unit.symbol if unit else '')) if amount else '%s %s' % (floatdot(0, unit.precision if unit else 2), unit.symbol if unit else '')


@register.filter
def balance(account):
    if account.closed:
        balance = 0
    else:
        balance = account.entries.filter(day__lte=date.today()).aggregate(Sum('amount'))['amount__sum']
    return colorfy(balance, account.unit)


@register.filter
def outstanding(account):
    if account.closed:
        outstanding = 0
    else:
        outstanding = account.entries.filter(day__gt=date.today()).filter(day__lte=get_last_date_current_month()).aggregate(Sum('amount'))['amount__sum']
    return colorfy(outstanding, account.unit)


@register.filter
def accounts(obj, ledger):
    if isinstance(obj, Category):
        return Account.objects.filter((Q(entries__in=obj.entries.all()) | Q(category=obj)) & Q(ledger=ledger)).distinct()
    elif isinstance(obj, Tag):
        return Account.objects.filter(Q(entries__in=obj.entries.all()) & Q(ledger=ledger)).distinct()
    else:
        return []


@register.filter
def sumbalance(unit, user):
    sum_balance = 0
    for account in Account.objects.filter(Q(unit=unit) & Q(ledgers__user=user)):
        balance = account.entries.filter(day__lte=date.today()).aggregate(Sum('amount'))['amount__sum']
        sum_balance += balance if balance else 0
    return colorfy(sum_balance, unit)


@register.filter
def sumentries(entries, unit=None):
    if unit:
        return colorfy(sum([entry.amount for entry in entries]), unit)
    else:
        sums = {}
        for entry in entries:
            if not entry.account.unit in sums:
                sums[entry.account.unit] = 0
            sums[entry.account.unit] += entry.amount
        return mark_safe('<ul>%s</ul>' % ''.join('<li>%s</li>' % colorfy(v, k) for k, v in sums.items()))


@register.filter
def sumoutstanding(unit, user):
    sum_outstanding = 0
    for account in Account.objects.filter(Q(unit=unit) & Q(ledgers__user=user)):
        outstanding = account.entries.filter(day__gt=date.today()).filter(day__lte=get_last_date_current_month()).aggregate(Sum('amount'))['amount__sum']
        sum_outstanding += outstanding if outstanding else 0
    return colorfy(sum_outstanding, unit)
