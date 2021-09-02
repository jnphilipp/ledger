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

from accounts.models import Entry
from categories.models import Category, Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from units.models import Unit
from users.models import Ledger


@login_required
def categories(request, unit, year=None, month=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    unit = get_object_or_404(Unit, slug=unit)
    accounts = ledger.accounts.filter(unit=unit)

    data = None
    if month and year:
        days = Entry.objects.filter(
            Q(account__in=accounts) & Q(day__year=year) & Q(day__month=month)
        ).dates("day", "day")
        data = {
            "xAxis": {
                "categories": [
                    "%s. %s" % (d.strftime("%d"), d.strftime("%B")) for d in days
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
        accounts = ledger.accounts.all()
        categories = (
            Category.objects.exclude(accounts__in=accounts)
            .filter(
                Q(entries__account__in=accounts)
                & Q(entries__account__unit=unit)
                & Q(entries__day__year=year)
                & Q(entries__day__month=month)
            )
            .distinct()
        )
        for category in categories:
            entries = category.entries.filter(
                Q(account__in=accounts)
                & Q(account__unit=unit)
                & Q(day__year=year)
                & Q(day__month=month)
            )
            sdata = []
            for d in days:
                v = entries.filter(day__day=d.strftime("%d")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append(("%s. %s" % (d.strftime("%d"), d.strftime("%B")), v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    elif year:
        months = Entry.objects.filter(
            Q(account__in=accounts) & Q(day__year=year)
        ).dates("day", "month")
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
        accounts = ledger.accounts.all()
        categories = (
            Category.objects.exclude(accounts__in=accounts)
            .filter(
                Q(entries__account__in=accounts)
                & Q(entries__account__unit=unit)
                & Q(entries__day__year=year)
            )
            .distinct()
        )
        for category in categories:
            entries = category.entries.filter(
                Q(account__in=accounts) & Q(account__unit=unit) & Q(day__year=year)
            )
            sdata = []
            for m in months:
                v = entries.filter(day__month=m.strftime("%m")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((m.strftime("%B"), v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    else:
        years = Entry.objects.filter(account__in=accounts).dates("day", "year")
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

        accounts = ledger.accounts.all()
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
                v = entries.filter(day__year=y.strftime("%Y")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((y.strftime("%Y"), v))
            series.append({"name": category.name, "data": sdata})
        data["series"] = series
    return JsonResponse(data)


@login_required
def tags(request, unit, year=None, month=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    unit = get_object_or_404(Unit, slug=unit)
    accounts = ledger.accounts.filter(unit=unit)

    data = None
    if month and year:
        days = Entry.objects.filter(
            Q(account__in=accounts)
            & Q(tags__isnull=False)
            & Q(day__year=year)
            & Q(day__month=month)
        ).dates("day", "day")
        data = {
            "xAxis": {
                "categories": [
                    "%s. %s" % (d.strftime("%d"), d.strftime("%B")) for d in days
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

        accounts = ledger.accounts.all()
        series = []
        tags = Tag.objects.filter(
            Q(entries__account__in=accounts)
            & Q(entries__account__unit=unit)
            & Q(entries__day__year=year)
            & Q(entries__day__month=month)
        ).distinct()
        for tag in tags:
            entries = tag.entries.filter(
                Q(account__in=accounts)
                & Q(account__unit=unit)
                & Q(day__year=year)
                & Q(day__month=month)
            )
            sdata = []
            for d in days:
                v = entries.filter(day__day=d.strftime("%d")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append(("%s. %s" % (d.strftime("%d"), d.strftime("%B")), v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    elif year:
        months = Entry.objects.filter(
            Q(account__in=accounts) & Q(tags__isnull=False) & Q(day__year=year)
        ).dates("day", "month")
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

        accounts = ledger.accounts.all()
        series = []
        tags = Tag.objects.filter(
            Q(entries__account__in=accounts)
            & Q(entries__account__unit=unit)
            & Q(entries__day__year=year)
        ).distinct()
        for tag in tags:
            entries = tag.entries.filter(
                Q(account__in=accounts) & Q(account__unit=unit) & Q(day__year=year)
            )
            sdata = []
            for m in months:
                v = entries.filter(day__month=m.strftime("%m")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((m.strftime("%B"), v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    else:
        years = Entry.objects.filter(
            Q(account__in=accounts) & Q(tags__isnull=False)
        ).dates("day", "year")
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

        accounts = ledger.accounts.all()
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
                v = entries.filter(day__year=y.strftime("%Y")).aggregate(
                    sum=Sum("amount")
                )["sum"]
                sdata.append((y.strftime("%Y"), v))
            series.append({"name": tag.name, "data": sdata})
        data["series"] = series
    return JsonResponse(data)
