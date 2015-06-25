from accounts.functions.dates import get_last_date_current_month
from accounts.templatetags.accounts import register
from datetime import date
from django.utils.numberformat import format
from django.utils.safestring import mark_safe

@register.filter
def floatdot(value, decimal_pos=2):
    if not value:
        return format(0, ",", decimal_pos)
    else:
        return format(round(value, decimal_pos), ",", decimal_pos)
floatdot.is_safe = True

@register.filter(needs_autoescape=True)
def colorfy(amount, currency=None, autoescape=None):
    return mark_safe('<span class="%s">%s %s</span>' % ('green' if amount >= 0 else 'red', floatdot(amount, 2), currency.symbol if currency else ''))

@register.filter(needs_autoescape=True)
def balance(account, autoescape=None):
    balance = sum(entry.amount for entry in account.entry_set.filter(day__lte=date.today()))
    return colorfy(balance, account.unit)

@register.filter(needs_autoescape=True)
def outstanding(account, autoescape=None):
    outstanding = sum(entry.amount for entry in account.entry_set.filter(day__gt=date.today()).filter(day__lte=get_last_date_current_month()))
    return colorfy(outstanding, account.unit)