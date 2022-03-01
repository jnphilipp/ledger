# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Ledger Django ledger statistics views."""

from datetime import date
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from units.models import Unit

from ..models import Account, Entry
from ..models import Category, Tag


class StatisticsView(generic.base.TemplateView):
    """Statistics view."""

    template_name = "ledger/statistics.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super(StatisticsView, self).get_context_data(*args, **kwargs)

        if "unit" in self.kwargs:
            context["unit"] = get_object_or_404(Unit, code=self.kwargs["unit"])
            accounts = Account.objects.filter(unit=context["unit"])
        else:
            units = Unit.objects.filter(accounts__isnull=False).distinct()

            context["option_msg"] = _("Select a unit")
            context["options"] = [
                {"id": unit.code, "key": "unit", "value": unit.name} for unit in units
            ]

            return context

        if "chart" in self.kwargs:
            context["chart"] = self.kwargs["chart"]

            if context["chart"] == "tags":
                context["chart_name"] = _("Tags")
            elif context["chart"] == "categories":
                context["chart_name"] = _("Categories")
            else:
                return context
        else:
            context["option_msg"] = _("Select a chart")
            context["options"] = [
                {"id": "categories", "key": "chart", "value": _("Categories")},
                {"id": "tags", "key": "chart", "value": _("Tags")},
            ]

            return context

        if "year" in self.kwargs:
            context["year"] = self.kwargs["year"]
        else:
            years = Entry.objects.filter(account__in=accounts).dates("date", "year")
            if context["chart"] == "tags":
                years = years.filter(tags__isnull=False)

            context["option_msg"] = _("Select a year")
            context["options"] = [
                {"id": year.strftime("%Y"), "key": "year", "value": year.strftime("%Y")}
                for year in years
            ]

            return context

        if "month" in self.kwargs:
            context["month"] = self.kwargs["month"]
            context["month_name"] = date(
                year=context["year"], month=context["month"], day=1
            ).strftime("%B")
        else:
            months = (
                Entry.objects.filter(account__in=accounts)
                .filter(date__year=context["year"])
                .dates("date", "month")
            )
            if context["chart"] == "tags":
                months = months.filter(tags__isnull=False)

            context["option_msg"] = _("Select a month")
            context["options"] = [
                {
                    "id": month.strftime("%m"),
                    "key": "month",
                    "value": _(month.strftime("%B")),
                }
                for month in months
            ]

        return context


def categories(request, unit, year=None, month=None):
    """Statistics categories chart."""
    unit = get_object_or_404(Unit, code=unit)
    accounts = Account.objects.filter(unit=unit)

    data = None
    if month and year:
        dates = Entry.objects.filter(
            Q(account__in=accounts) & Q(date__year=year) & Q(date__month=month)
        ).dates("date", "day")
        data = {
            "xAxis": {
                "categories": [f"{d.strftime('%d')}." for d in dates],
                "title": {"text": _("Days")},
            },
            "yAxis": {
                "stackLabels": {"format": f"{{total:,.2f}} {unit.symbol}"},
                "labels": {"format": f"{{value}} {unit.symbol}"},
                "title": {"text": _("Loss and Profit")},
            },
            "tooltip": {"valueSuffix": unit.symbol},
        }

        series = []
        accounts = Account.objects.all()
        categories = (
            Category.objects.exclude(accounts__in=accounts)
            .filter(
                Q(entries__account__in=accounts)
                & Q(entries__account__unit=unit)
                & Q(entries__date__year=year)
                & Q(entries__date__month=month)
            )
            .distinct()
        )
        for category in categories:
            entries = category.entries.filter(
                Q(account__in=accounts)
                & Q(account__unit=unit)
                & Q(date__year=year)
                & Q(date__month=month)
            )
            sdata = []
            for d in dates:
                v = entries.filter(date__day=d.strftime("%d")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((f"{d.strftime('%d')}.", v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    elif year:
        months = Entry.objects.filter(
            Q(account__in=accounts) & Q(date__year=year)
        ).dates("date", "month")
        data = {
            "xAxis": {
                "categories": [_(m.strftime("%B")) for m in months],
                "title": {"text": _("Months")},
            },
            "yAxis": {
                "stackLabels": {"format": f"{{total:,.2f}} {unit.symbol}"},
                "labels": {"format": f"{{value}} {unit.symbol}"},
                "title": {"text": _("Loss and Profit")},
            },
            "tooltip": {"valueSuffix": unit.symbol},
        }

        series = []
        accounts = Account.objects.all()
        categories = (
            Category.objects.exclude(accounts__in=accounts)
            .filter(
                Q(entries__account__in=accounts)
                & Q(entries__account__unit=unit)
                & Q(entries__date__year=year)
            )
            .distinct()
        )
        for category in categories:
            entries = category.entries.filter(
                Q(account__in=accounts) & Q(account__unit=unit) & Q(date__year=year)
            )
            sdata = []
            for m in months:
                v = entries.filter(date__month=m.strftime("%m")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((_(m.strftime("%B")), v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    else:
        years = Entry.objects.filter(account__in=accounts).dates("date", "year")
        data = {
            "xAxis": {
                "categories": [y.strftime("%Y") for y in years],
                "title": {"text": _("Years")},
            },
            "yAxis": {
                "stackLabels": {"format": f"{{total:,.2f}} {unit.symbol}"},
                "labels": {"format": f"{{value}} {unit.symbol}"},
                "title": {"text": _("Loss and Profit")},
            },
            "tooltip": {"valueSuffix": unit.symbol},
        }

        accounts = Account.objects.all()
        series = []
        categories = (
            Category.objects.exclude(accounts__in=accounts)
            .filter(Q(entries__account__in=accounts) & Q(entries__account__unit=unit))
            .distinct()
        )
        for category in categories:
            entries = category.entries.filter(
                Q(account__in=accounts) & Q(account__unit=unit)
            )
            sdata = []
            for y in years:
                v = entries.filter(date__year=y.strftime("%Y")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((y.strftime("%Y"), v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    return JsonResponse(data)


def tags(request, unit, year=None, month=None):
    """Statistics tag chart."""
    unit = get_object_or_404(Unit, code=unit)
    accounts = Account.objects.filter(unit=unit)

    data = None
    if month and year:
        dates = Entry.objects.filter(
            Q(account__in=accounts)
            & Q(tags__isnull=False)
            & Q(date__year=year)
            & Q(date__month=month)
        ).dates("date", "day")
        data = {
            "xAxis": {
                "categories": [f"{d.strftime('%d')}." for d in dates],
                "title": {"text": _("Days")},
            },
            "yAxis": {
                "stackLabels": {"format": f"{{total:,.2f}} {unit.symbol}"},
                "labels": {"format": f"{{value}} {unit.symbol}"},
                "title": {"text": _("Loss and Profit")},
            },
            "tooltip": {"valueSuffix": unit.symbol},
        }

        accounts = Account.objects.all()
        series = []
        tags = Tag.objects.filter(
            Q(entries__account__in=accounts)
            & Q(entries__account__unit=unit)
            & Q(entries__date__year=year)
            & Q(entries__date__month=month)
        ).distinct()
        for tag in tags:
            entries = tag.entries.filter(
                Q(account__in=accounts)
                & Q(account__unit=unit)
                & Q(date__year=year)
                & Q(date__month=month)
            )
            sdata = []
            for d in dates:
                v = entries.filter(date__day=d.strftime("%d")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((f"{d.strftime('%d')}", v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    elif year:
        months = Entry.objects.filter(
            Q(account__in=accounts) & Q(tags__isnull=False) & Q(date__year=year)
        ).dates("date", "month")
        data = {
            "xAxis": {
                "categories": [_(m.strftime("%B")) for m in months],
                "title": {"text": _("Months")},
            },
            "yAxis": {
                "stackLabels": {"format": f"{{total:,.2f}} {unit.symbol}"},
                "labels": {"format": f"{{value}} {unit.symbol}"},
                "title": {"text": _("Loss and Profit")},
            },
            "tooltip": {"valueSuffix": unit.symbol},
        }

        accounts = Account.objects.all()
        series = []
        tags = Tag.objects.filter(
            Q(entries__account__in=accounts)
            & Q(entries__account__unit=unit)
            & Q(entries__date__year=year)
        ).distinct()
        for tag in tags:
            entries = tag.entries.filter(
                Q(account__in=accounts) & Q(account__unit=unit) & Q(date__year=year)
            )
            sdata = []
            for m in months:
                v = entries.filter(date__month=m.strftime("%m")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((_(m.strftime("%B")), v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    else:
        years = Entry.objects.filter(
            Q(account__in=accounts) & Q(tags__isnull=False)
        ).dates("date", "year")
        data = {
            "xAxis": {
                "categories": [y.strftime("%Y") for y in years],
                "title": {"text": _("Years")},
            },
            "yAxis": {
                "stackLabels": {"format": f"{{total:,.2f}} {unit.symbol}"},
                "labels": {"format": f"{{value}} {unit.symbol}"},
                "title": {"text": _("Loss and Profit")},
            },
            "tooltip": {"valueSuffix": unit.symbol},
        }

        accounts = Account.objects.all()
        series = []
        tags = Tag.objects.filter(
            Q(entries__account__in=accounts) & Q(entries__account__unit=unit)
        ).distinct()
        for tag in tags:
            entries = tag.entries.filter(
                Q(account__in=accounts) & Q(account__unit=unit)
            )
            sdata = []
            for y in years:
                v = entries.filter(date__year=y.strftime("%Y")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((y.strftime("%Y"), v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    return JsonResponse(data)
