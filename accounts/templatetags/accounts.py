# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# This file is part of ledger.
#
# ledger is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ledger is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ledger.  If not, see <http://www.gnu.org/licenses/>.

from accounts.models import Account, Entry
from datetime import date
from django.db.models import F, Sum
from django.template import Library
from django.template.defaultfilters import floatformat
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from ledger.dates import get_last_date_current_month
from units.models import Unit


register = Library()


@register.filter
def colorfy(amount, unit=None):
    precision = unit.precision if unit else 2
    symbol = unit.symbol if unit else ""
    if amount:
        return mark_safe(
            f'<span class="{"green" if amount >= 0 else "red"}"'
            + f">{floatformat(amount, precision)} {symbol}</span>"
        )
    else:
        return f"{floatformat(0, precision)} {symbol}".strip()


@register.filter
def balance(obj):
    if isinstance(obj, Account):
        if obj.closed:
            balance = 0
        else:
            balance = obj.entries.filter(date__lte=date.today()).aggregate(
                Sum("amount")
            )["amount__sum"]
        unit = obj.unit
    elif isinstance(obj, Unit):
        balance = Entry.objects.filter(account__unit=obj).filter(date__lte=date.today()).aggregate(
            sum=Sum(F("amount") + F("fees"))
        )["sum"]
        unit = obj
    else:
        balance = 0
        unit = None

    return colorfy(balance, unit)


@register.filter
def has_tags(account):
    return account.entries.filter(tags__isnull=False).count() > 0


@register.filter
def outstanding(account):
    if account.closed:
        outstanding = 0
    else:
        outstanding = (
            account.entries.filter(date__gt=date.today())
            .filter(date__lte=get_last_date_current_month())
            .aggregate(Sum("amount"))["amount__sum"]
        )
    return colorfy(outstanding, account.unit)


@register.inclusion_tag("accounts/partials/_balances.html", takes_context=True)
def balance(context, account=None):
    values = []

    if account:
        entries = account.entries.all()
    else:
        entries = Entry.objects.all()

    ids = set(entries.values_list("account__unit", flat=True))
    for unit in Unit.objects.filter(id__in=ids):
        e = entries.filter(account__unit=unit)
        balance = e.filter(date__lte=date.today()).aggregate(
            sum=Sum(F("amount") + F("fees"))
        )["sum"]
        outstanding = (
            e.filter(date__gt=date.today())
            .filter(date__lte=get_last_date_current_month())
            .aggregate(sum=Sum(F("amount") + F("fees")))["sum"]
        )

        if account:
            values.append(
                {
                    "balance": colorfy(balance, unit),
                    "outstanding": colorfy(outstanding, unit),
                }
            )
        else:
            accounts = []
            for a in unit.accounts.filter(closed=False):
                b = a.entries.filter(date__lte=date.today()).aggregate(
                    sum=Sum(F("amount") + F("fees"))
                )["sum"]
                o = (
                    a.entries.filter(date__gt=date.today())
                    .filter(date__lte=get_last_date_current_month())
                    .aggregate(sum=Sum(F("amount") + F("fees")))["sum"]
                )
                if not o:
                    o = 0.0
                accounts.append(
                    {
                        "name": a.name,
                        "balance": f"{floatformat(b, unit.precision)} "
                        + f"{unit.symbol}",
                        "outstanding": f"{floatformat(o, unit.precision)} "
                        + f"{unit.symbol}",
                    }
                )

            values.append(
                {
                    "balance": colorfy(balance, unit),
                    "outstanding": colorfy(outstanding, unit),
                    "accounts": accounts,
                }
            )
    return {"values": values}
