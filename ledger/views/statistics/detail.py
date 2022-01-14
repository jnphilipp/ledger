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
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from units.models import Unit


class StatisticsView(generic.base.TemplateView):
    template_name = "ledger/statistics.html"

    def get_context_data(self, *args, **kwargs):
        context = super(StatisticsView, self).get_context_data(*args, **kwargs)

        if "unit" in self.kwargs:
            context["unit"] = get_object_or_404(Unit, slug=self.kwargs["unit"])
            accounts = Account.objects.filter(unit=context["unit"])
        else:
            units = Unit.objects.filter(accounts__isnull=False).distinct()

            context["option_msg"] = _("Select a unit")
            context["options"] = [
                {"id": unit.slug, "key": "unit", "value": unit.name} for unit in units
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
