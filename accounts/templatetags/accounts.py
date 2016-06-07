# -*- coding: utf-8 -*-


from accounts.models import Account
from categories.models import Category, Tag
from datetime import date
from django.db.models import Q
from django.template import Library
from django.utils.numberformat import format
from django.utils.safestring import mark_safe
from ledger.functions.dates import get_last_date_current_month

register = Library()


@register.filter(is_safe=True)
def floatdot(value, precision=2):
    return format(0, ",", precision) if not value else format(round(value, precision), ",", precision)

@register.filter(needs_autoescape=True)
def colorfy(amount, unit=None, autoescape=None):
    return mark_safe('<span class="%s">%s %s</span>' % ('green' if amount >= 0 else 'red', floatdot(amount, unit.precision if unit else 2), unit.symbol if unit else '')) if amount else '%s %s' % (floatdot(0, unit.precision if unit else 2), unit.symbol if unit else '')

@register.filter(needs_autoescape=True)
def balance(account, autoescape=None):
    balance = sum(entry.amount for entry in account.entries.filter(day__lte=date.today()))
    return colorfy(balance, account.unit) if autoescape else balance

@register.filter(needs_autoescape=True)
def outstanding(account, autoescape=None):
    outstanding = sum(entry.amount for entry in account.entries.filter(day__gt=date.today()).filter(day__lte=get_last_date_current_month()))
    return colorfy(outstanding, account.unit) if autoescape else outstanding

@register.filter
def accounts(obj, user):
    if isinstance(obj, Category):
        return Account.objects.filter(Q(entries__in=obj.entries.all()) & Q(ledgers__user=user)).distinct()
    elif isinstance(obj, Tag):
        return Account.objects.filter(Q(entries__in=obj.entries.all()) & Q(ledgers__user=user)).distinct()
    else:
        return []

@register.filter(needs_autoescape=True)
def sumbalance(unit, user, autoescape=None):
    sum_balance = 0
    for account in Account.objects.filter(Q(unit=unit) & Q(ledgers__user=user)):
        sum_balance += balance(account)
    return colorfy(sum_balance, unit)

@register.filter(needs_autoescape=True)
def sumentries(entries, unit=None, autoescape=None):
    if unit:
        return colorfy(sum([entry.amount for entry in entries]), unit)
    else:
        sums = {}
        for entry in entries:
            if not entry.account.unit in sums:
                sums[entry.account.unit] = 0
            sums[entry.account.unit] += entry.amount
        return mark_safe('<ul>%s</ul>' % ''.join('<li>%s</li>' % colorfy(v, k) for k,v in sums.items()))

@register.filter(needs_autoescape=True)
def sumoutstanding(unit, user, autoescape=None):
    sum_outstanding = 0
    for account in Account.objects.filter(Q(unit=unit) & Q(ledgers__user=user)):
        sum_outstanding += outstanding(account)
    return colorfy(sum_outstanding, unit)
