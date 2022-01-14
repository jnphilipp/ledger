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

from categories.models import Category, Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from units.models import Unit


def statistics(request, slug, year=None):
    tag = get_object_or_404(Tag, slug=slug)

    units = set(
        tag.entries.values_list(
            "account__unit", flat=True
        )
    )
    units = Unit.objects.filter(id__in=units)
    symbol = units[0].symbol if units.count() == 1 else ""

    if year:
        months = tag.entries.filter(date__year=year).dates("date", "month")

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
        categories = Category.objects.filter(
            Q(entries__tags=tag)
            & Q(entries__date__year=year)
        ).distinct()
        for category in categories:
            for unit in units:
                entries = tag.entries.filter(
                    Q(category=category) & Q(account__unit=unit) & Q(date__year=year)
                )
                sdata = []
                for m in months:
                    v = entries.filter(date__month=m.strftime("%m")).aggregate(
                        sum=Sum("amount")
                    )["sum"]
                    sdata.append((m.strftime("%B"), v))
                if entries.count() > 0:
                    series.append(
                        {
                            "name": category.name,
                            "data": sdata,
                            "tooltip": {"valueSuffix": unit.symbol},
                            "type": "column",
                            "stack": unit.name,
                        }
                    )

        for unit in units:
            amount_sum = tag.entries.filter(
                Q(account__unit=unit) & Q(date__year=year)
            ).aggregate(sum=Sum("amount"))["sum"]
            if amount_sum is None:
                continue
            series.append(
                {
                    "name": _("Average %(unit)s") % {"unit": unit.name},
                    "type": "spline",
                    "data": [amount_sum / months.count() for m in months],
                    "tooltip": {"valueSuffix": unit.symbol},
                }
            )
        data["series"] = series
    else:
        years = tag.entries.dates("date", "year")

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
        categories = Category.objects.filter(entries__tags=tag).distinct()
        for category in categories:
            for unit in units:
                entries = tag.entries.filter(
                    Q(category=category) & Q(account__unit=unit)
                )
                sdata = []
                for y in years:
                    v = entries.filter(date__year=y.strftime("%Y")).aggregate(
                        sum=Sum("amount")
                    )["sum"]
                    sdata.append((y.strftime("%Y"), v))
                if entries.count() > 0:
                    series.append(
                        {
                            "name": category.name,
                            "data": sdata,
                            "tooltip": {"valueSuffix": unit.symbol},
                            "type": "column",
                            "stack": unit.name,
                        }
                    )

        for unit in units:
            avg = tag.entries.filter(account__unit=unit).aggregate(sum=Sum("amount"))["sum"] / len(years)
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
