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
from categories.models import Category, Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from units.models import Unit


def categories(request, unit, year=None, month=None):
    unit = get_object_or_404(Unit, slug=unit)
    accounts = Account.objects.filter(unit=unit)

    data = None
    if month and year:
        dates = Entry.objects.filter(
            Q(account__in=accounts) & Q(date__year=year) & Q(date__month=month)
        ).dates("date", "day")
        data = {
            "xAxis": {
                "categories": [
                    "%s. %s" % (d.strftime("%d"), d.strftime("%B")) for d in dates
                ],
                "title": {"text": str(_("Days"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % unit.symbol},
                "labels": {"format": "{value}%s" % unit.symbol},
                "title": {"text": str(_("Loss and Profit"))},
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
                sdata.append(("%s. %s" % (d.strftime("%d"), d.strftime("%B")), v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    elif year:
        months = Entry.objects.filter(
            Q(account__in=accounts) & Q(date__year=year)
        ).dates("date", "month")
        data = {
            "xAxis": {
                "categories": [m.strftime("%B") for m in months],
                "title": {"text": str(_("Months"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % unit.symbol},
                "labels": {"format": "{value}%s" % unit.symbol},
                "title": {"text": str(_("Loss and Profit"))},
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
                sdata.append((m.strftime("%B"), v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    else:
        years = Entry.objects.filter(account__in=accounts).dates("date", "year")
        data = {
            "xAxis": {
                "categories": [y.strftime("%Y") for y in years],
                "title": {"text": str(_("Years"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % unit.symbol},
                "labels": {"format": "{value}%s" % unit.symbol},
                "title": {"text": str(_("Loss and Profit"))},
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
    unit = get_object_or_404(Unit, slug=unit)
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
                "categories": [
                    "%s. %s" % (d.strftime("%d"), d.strftime("%B")) for d in dates
                ],
                "title": {"text": str(_("Days"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % unit.symbol},
                "labels": {"format": "{value}%s" % unit.symbol},
                "title": {"text": str(_("Loss and Profit"))},
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
                sdata.append(("%s. %s" % (d.strftime("%d"), d.strftime("%B")), v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    elif year:
        months = Entry.objects.filter(
            Q(account__in=accounts) & Q(tags__isnull=False) & Q(date__year=year)
        ).dates("date", "month")
        data = {
            "xAxis": {
                "categories": [m.strftime("%B") for m in months],
                "title": {"text": str(_("Months"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % unit.symbol},
                "labels": {"format": "{value}%s" % unit.symbol},
                "title": {"text": str(_("Loss and Profit"))},
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
                sdata.append((m.strftime("%B"), v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    else:
        years = Entry.objects.filter(
            Q(account__in=accounts) & Q(tags__isnull=False)
        ).dates("date", "year")
        data = {
            "xAxis": {
                "categories": [y.strftime("%Y") for y in years],
                "title": {"text": str(_("Years"))},
            },
            "yAxis": {
                "stackLabels": {"format": "{total:,.2f}%s" % unit.symbol},
                "labels": {"format": "{value}%s" % unit.symbol},
                "title": {"text": str(_("Loss and Profit"))},
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
