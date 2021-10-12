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

from accounts.models import Account
from categories.models import Category
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from units.models import Unit


@login_required
def statistics(request, slug, year=None):
    category = get_object_or_404(Category, slug=slug)

    units = set(
        category.entries.values_list(
            "account__unit", flat=True
        )
    )
    units = Unit.objects.filter(id__in=units)
    symbol = units[0].symbol if units.count() == 1 else ""

    if year:
        months = category.entries.filter(day__year=year).dates("day", "month")
        data = {
            "xAxis": {
                "categories": [m.strftime("%B") for m in months],
                "title": {"text": str(_("Months"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % symbol},
                "labels": {"format": "{value}%s" % symbol},
                "title": {"text": str(_("Loss and Profit"))},
            },
            "tooltip": {"valueSuffix": symbol},
        }

        series = []
        accounts = Account.objects.filter(
            Q(entries__category=category)
            & Q(entries__day__year=year)
        ).distinct()
        for account in accounts:
            entries = category.entries.filter(Q(account=account) & Q(day__year=year))
            sdata = []
            for m in months:
                y = entries.filter(day__month=m.strftime("%m")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((m.strftime("%B"), y))
            series.append(
                {
                    "name": account.name,
                    "data": sdata,
                    "tooltip": {"valueSuffix": account.unit.symbol},
                    "type": "column",
                    "stack": account.unit.name,
                }
            )

        for unit in units:
            amount = category.entries.filter(
                Q(account__unit=unit) & Q(day__year=year)
            ).aggregate(sum=Sum("amount"))
            if amount["sum"]:
                avg = amount["sum"] / len(months)
                series.append(
                    {
                        "name": _("Average %(unit)s") % {"unit": unit.name},
                        "type": "spline",
                        "data": [avg for m in months],
                        "tooltip": {"valueSuffix": unit.symbol},
                    }
                )
        data["series"] = series
    else:
        years = category.entries.dates("day", "year")
        data = {
            "xAxis": {
                "categories": [y.strftime("%Y") for y in years],
                "title": {"text": str(_("Years"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % symbol},
                "labels": {"format": "{value}%s" % symbol},
                "title": {"text": str(_("Loss and Profit"))},
            },
            "tooltip": {"valueSuffix": symbol},
        }

        series = []
        accounts = Account.objects.filter(entries__category=category).distinct()
        for account in accounts:
            entries = category.entries.filter(account=account)
            sdata = []
            for y in years:
                v = entries.filter(day__year=y.strftime("%Y")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((y.strftime("%Y"), v))
            series.append(
                {
                    "name": account.name,
                    "data": sdata,
                    "tooltip": {"valueSuffix": account.unit.symbol},
                    "type": "column",
                    "stack": account.unit.name,
                }
            )

        for unit in units:
            avg = category.entries.filter(account__unit=unit).aggregate(sum=Sum("amount"))["sum"] / len(years)
            series.append(
                {
                    "name": _("Average %(unit)s") % {"unit": unit.name},
                    "type": "spline",
                    "data": [avg for y in years],
                    "tooltip": {"valueSuffix": unit.symbol},
                }
            )
        data["series"] = series
    return JsonResponse(data)
