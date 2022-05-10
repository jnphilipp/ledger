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
"""Ledger Django app budget views."""

import json

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Func, Q, Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic
from typing import Any, Dict, List, Set, Tuple
from units.models import Unit
from units.templatetags.units import unitcolorfy

from ..forms import BudgetForm
from ..models import Account, Budget, Entry


class DetailView(generic.DetailView):
    """Budget detail view."""

    model = Budget

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(*args, **kwargs)

        if Entry.objects.count() == 0:
            return context

        years = Entry.objects.dates("date", "year")
        context["years"] = [y.year for y in years]

        if "year" in self.kwargs:
            year = self.kwargs["year"]
        else:
            y = timezone.now().year
            if y in context["years"]:
                year = y
            else:
                year = context["years"][-1]

        entry_ids = set()
        units = set()
        series = ({}, {})
        drilldown = ({}, {})

        footer = []
        footer.append(_("Sum"))
        footer.append({})
        footer.append({})
        income = self.calculate_part(
            self.object.income_tags.annotate(
                name_lower=Func(F("name"), function="LOWER")
            ).order_by("name_lower"),
            year,
            "income",
            _("Income"),
            entry_ids,
            series,
            drilldown,
            footer,
            1,
            units,
        )

        footer.append(_("Sum"))
        footer.append({})
        footer.append({})
        consumption = self.calculate_part(
            self.object.consumption_tags.annotate(
                name_lower=Func(F("name"), function="LOWER")
            ).order_by("name_lower"),
            year,
            "consumption",
            _("Consumption"),
            entry_ids,
            series,
            drilldown,
            footer,
            4,
            units,
        )

        footer.append(_("Sum"))
        footer.append({})
        footer.append({})
        insurance = self.calculate_part(
            self.object.insurance_tags.annotate(
                name_lower=Func(F("name"), function="LOWER")
            ).order_by("name_lower"),
            year,
            "insurance",
            _("Insurance"),
            entry_ids,
            series,
            drilldown,
            footer,
            7,
            units,
        )

        footer.append(_("Sum"))
        footer.append({})
        footer.append({})
        savings = self.calculate_part(
            self.object.savings_tags.annotate(
                name_lower=Func(F("name"), function="LOWER")
            ).order_by("name_lower"),
            year,
            "savings",
            _("Savings"),
            entry_ids,
            series,
            drilldown,
            footer,
            10,
            units,
        )

        for unit in units:
            msum = (
                Entry.objects.exclude(pk__in=entry_ids)
                .filter(
                    Q(category__name="Portfolio")
                    & Q(date__year=year)
                    & Q(account__unit=unit)
                )
                .annotate(total=F("amount") + F("fees"))
                .aggregate(Sum("total"))["total__sum"]
            )
            if unit in series[0]:
                series[0][unit]["data"].append(
                    {
                        "name": str(_("Portfolio")),
                        "v": msum / 12 if msum else 0.0,
                        "y": abs(msum) / 12 if msum else 0.0,
                        "drilldown": "p",
                    }
                )
                series[1][unit]["data"].append(
                    {
                        "name": str(_("Portfolio")),
                        "v": msum if msum else 0.0,
                        "y": abs(msum) if msum else 0.0,
                        "drilldown": "p",
                    }
                )

            if not msum:
                del series[0][unit]["data"][-1]["drilldown"]
                del series[1][unit]["data"][-1]["drilldown"]
            else:
                drilldown[0][unit]["p"] = self.drilldown(_("Portfolio"), "p", unit)
                drilldown[1][unit]["p"] = self.drilldown(_("Portfolio"), "p", unit)
                portfolio = {}
                entries = (
                    Entry.objects.exclude(pk__in=entry_ids)
                    .filter(
                        Q(category__name="Portfolio")
                        & Q(date__year=year)
                        & Q(account__unit=unit)
                    )
                    .annotate(total=F("amount") + F("fees"))
                )
                for e in entries:
                    if e.pk not in entry_ids:
                        t = (
                            e.tags.exclude(
                                pk__in=self.object.income_tags.all().values("pk")
                            )
                            .exclude(
                                pk__in=self.object.consumption_tags.all().values("pk")
                            )
                            .exclude(
                                pk__in=self.object.insurance_tags.all().values("pk")
                            )
                            .exclude(pk__in=self.object.savings_tags.all().values("pk"))
                            .first()
                        )
                        if t:
                            if t.pk not in portfolio:
                                portfolio[t.pk] = {"name": t.name, "amount": 0}
                            portfolio[t.pk]["amount"] += e.total
                        else:
                            if "rest" not in portfolio:
                                portfolio["rest"] = {"name": _("Rest"), "amount": 0}
                            portfolio["rest"]["amount"] += e.total
                        entry_ids.add(e.pk)

                for k, v in portfolio.items():
                    if v:
                        drilldown[0][unit]["p"]["data"].append(
                            {
                                "name": str(v["name"]),
                                "v": v["amount"] / 12,
                                "y": abs(v["amount"]) / 12,
                                "drilldown": "p_%s" % k,
                            }
                        )
                        drilldown[1][unit]["p"]["data"].append(
                            {
                                "name": str(v["name"]),
                                "v": v["amount"],
                                "y": abs(v["amount"]),
                                "drilldown": "p_%s" % k,
                            }
                        )

            msum = (
                Entry.objects.exclude(pk__in=entry_ids)
                .exclude(category__accounts__in=Account.objects.all())
                .exclude(category__name="Portfolio")
                .filter(Q(date__year=year) & Q(account__unit=unit))
                .annotate(total=F("amount") + F("fees"))
                .aggregate(Sum("total"))["total__sum"]
            )
            if unit in series[0]:
                series[0][unit]["data"].append(
                    {
                        "name": str(_("Rest")),
                        "v": msum / 12 if msum else 0.0,
                        "y": abs(msum) / 12 if msum else 0.0,
                        "drilldown": "r",
                    }
                )
                series[1][unit]["data"].append(
                    {
                        "name": str(_("Rest")),
                        "v": msum if msum else 0.0,
                        "y": abs(msum) if msum else 0.0,
                        "drilldown": "r",
                    }
                )

            if not msum:
                del series[0][unit]["data"][-1]["drilldown"]
                del series[1][unit]["data"][-1]["drilldown"]
            else:
                drilldown[0][unit]["r"] = self.drilldown(_("Rest"), "r", unit)
                drilldown[1][unit]["r"] = self.drilldown(_("Rest"), "r", unit)
                drilldown[0][unit]["r2"] = self.drilldown(_("Rest"), "r2", unit)
                drilldown[1][unit]["r2"] = self.drilldown(_("Rest"), "r2", unit)
                rest = {"r2": {"name": _("Rest"), "amount": 0, "categories": {}}}
                entries = (
                    Entry.objects.exclude(pk__in=entry_ids)
                    .exclude(category__accounts__in=Account.objects.all())
                    .exclude(category__name="Portfolio")
                    .filter(Q(date__year=year) & Q(account__unit=unit))
                    .annotate(total=F("amount") + F("fees"))
                )
                for e in entries:
                    if e.pk not in entry_ids:
                        t = e.tags.first()
                        if t:
                            if t.pk not in rest:
                                rest[t.pk] = {
                                    "name": t.name,
                                    "amount": 0,
                                    "categories": {},
                                }
                            rest[t.pk]["amount"] += e.total

                            if e.category.pk not in rest[t.pk]["categories"]:
                                rest[t.pk]["categories"][e.category.pk] = {
                                    "name": e.category.name,
                                    "amount": 0,
                                }

                                id = f"r_{t.pk}"
                                drilldown[0][unit][id] = self.drilldown(
                                    e.category.name, id, unit
                                )
                                drilldown[1][unit][id] = self.drilldown(
                                    e.category.name, id, unit
                                )
                            rest[t.pk]["categories"][e.category.pk]["amount"] += e.total
                        else:
                            rest["r2"]["amount"] += e.total
                            if e.category.pk not in rest["r2"]["categories"]:
                                rest["r2"]["categories"][e.category.pk] = {
                                    "name": e.category.name,
                                    "amount": 0,
                                }
                                drilldown[0][unit]["r_r2"] = self.drilldown(
                                    e.category.name, "r_r2", unit
                                )
                                drilldown[1][unit]["r_r2"] = self.drilldown(
                                    e.category.name, "r_r2", unit
                                )
                            rest["r2"]["categories"][e.category.pk]["amount"] += e.total
                        entry_ids.add(e.pk)

                for k, v in rest.items():
                    if v:
                        drilldown[0][unit]["r"]["data"].append(
                            {
                                "name": str(v["name"]),
                                "v": v["amount"] / 12,
                                "y": abs(v["amount"]) / 12,
                                "drilldown": "r_%s" % k,
                            }
                        )
                        drilldown[1][unit]["r"]["data"].append(
                            {
                                "name": str(v["name"]),
                                "v": v["amount"],
                                "y": abs(v["amount"]),
                                "drilldown": "r_%s" % k,
                            }
                        )
                        for category, v2 in v["categories"].items():
                            if v2["amount"]:
                                drilldown[0][unit]["r_%s" % k]["data"].append(
                                    {
                                        "name": str(v2["name"]),
                                        "v": v2["amount"] / 12,
                                        "y": abs(v2["amount"]) / 12,
                                    }
                                )
                                drilldown[1][unit]["r_%s" % k]["data"].append(
                                    {
                                        "name": str(v2["name"]),
                                        "v": v2["amount"],
                                        "y": abs(v2["amount"]),
                                    }
                                )

        footer = [footer.copy() for unit in units]
        for i, unit in enumerate(units):
            if i > 0:
                footer[i][0] = footer[i][3] = footer[i][6] = footer[i][9] = ""

            footer.append(
                ["", "", "", "", "", "", "", "", "", _("Sum") if i == 0 else "", 0, 0]
            )
            footer[-1][10] = (
                (footer[i][1][unit] if unit in footer[i][1] else 0)
                + (footer[i][4][unit] if unit in footer[i][4] else 0)
                + (footer[i][7][unit] if unit in footer[i][7] else 0)
                + (footer[i][10][unit] if unit in footer[i][10] else 0)
            )
            footer[-1][11] = (
                (footer[i][2][unit] if unit in footer[i][2] else 0)
                + (footer[i][5][unit] if unit in footer[i][5] else 0)
                + (footer[i][8][unit] if unit in footer[i][8] else 0)
                + (footer[i][11][unit] if unit in footer[i][11] else 0)
            )

            footer[i][1] = (
                unitcolorfy(footer[i][1][unit], unit) if unit in footer[i][1] else ""
            )
            footer[i][2] = (
                unitcolorfy(footer[i][2][unit], unit) if unit in footer[i][2] else ""
            )
            footer[i][4] = (
                unitcolorfy(footer[i][4][unit], unit) if unit in footer[i][4] else ""
            )
            footer[i][5] = (
                unitcolorfy(footer[i][5][unit], unit) if unit in footer[i][5] else ""
            )
            footer[i][7] = (
                unitcolorfy(footer[i][7][unit], unit) if unit in footer[i][7] else ""
            )
            footer[i][8] = (
                unitcolorfy(footer[i][8][unit], unit) if unit in footer[i][8] else ""
            )
            footer[i][10] = (
                unitcolorfy(footer[i][10][unit], unit) if unit in footer[i][10] else ""
            )
            footer[i][11] = (
                unitcolorfy(footer[i][11][unit], unit) if unit in footer[i][11] else ""
            )
            footer[-1][10] = unitcolorfy(footer[-1][10], unit)
            footer[-1][11] = unitcolorfy(footer[-1][11], unit)

        for i, unit in enumerate(units):
            footer.append(
                ["", "", "", "", "", "", "", "", "", _("Rest") if i == 0 else "", 0, 0]
            )
            footer[-1][10] = unitcolorfy(series[0][unit]["data"][-1]["v"], unit)
            footer[-1][11] = unitcolorfy(series[1][unit]["data"][-1]["v"], unit)

            footer.append(
                [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    _("Portfolio") if i == 0 else "",
                    0,
                    0,
                ]
            )
            footer[-1][10] = unitcolorfy(series[0][unit]["data"][-2]["v"], unit)
            footer[-1][11] = unitcolorfy(series[1][unit]["data"][-2]["v"], unit)

            total = (
                Entry.objects.exclude(category__accounts__in=Account.objects.all())
                .filter(Q(account__unit=unit) & Q(date__year=year))
                .annotate(total=F("amount") + F("fees"))
                .aggregate(Sum("total"))["total__sum"]
            )
            footer.append(
                ["", "", "", "", "", "", "", "", "", _("Total") if i == 0 else "", 0, 0]
            )
            footer[-1][10] = unitcolorfy(total / 12, unit)
            footer[-1][11] = unitcolorfy(total, unit)

        table = []
        for i in range(
            max(len(income), len(consumption), len(insurance), len(savings))
        ):
            row = []
            if i < len(income):
                row.append(
                    [income[i]["pk"], income[i]["name"]] if income[i]["name"] else ""
                )
                row.append(income[i]["monthly"])
                row.append(income[i]["yearly"])
            else:
                row.append("")
                row.append("")
                row.append("")
            if i < len(consumption):
                row.append(
                    [consumption[i]["pk"], consumption[i]["name"]]
                    if consumption[i]["name"]
                    else ""
                )
                row.append(consumption[i]["monthly"])
                row.append(consumption[i]["yearly"])
            else:
                row.append("")
                row.append("")
                row.append("")
            if i < len(insurance):
                row.append(
                    [insurance[i]["pk"], insurance[i]["name"]]
                    if insurance[i]["name"]
                    else ""
                )
                row.append(insurance[i]["monthly"])
                row.append(insurance[i]["yearly"])
            else:
                row.append("")
                row.append("")
                row.append("")
            if i < len(savings):
                row.append(
                    [savings[i]["pk"], savings[i]["name"]] if savings[i]["name"] else ""
                )
                row.append(savings[i]["monthly"])
                row.append(savings[i]["yearly"])
            else:
                row.append("")
                row.append("")
                row.append("")
            table.append(row)

        context["footer"] = footer
        context["table"] = table
        context["units"] = units
        context["year"] = year
        if len(series[0]) == 1:
            monthly = json.dumps([v for k, v in series[0].items()])
            yearly = json.dumps([v for k, v in series[1].items()])
            dmonthly = json.dumps(
                {
                    "series": [
                        s
                        for k, v in drilldown[0].items()
                        for k2, s in drilldown[0][k].items()
                    ]
                }
            )
            dyearly = json.dumps(
                {
                    "series": [
                        s
                        for k, v in drilldown[1].items()
                        for k2, s in drilldown[1][k].items()
                    ]
                }
            )
        else:
            monthly = dict((k.id, json.dumps([v])) for k, v in series[0].items())
            yearly = dict((k.id, json.dumps([v])) for k, v in series[1].items())
            dmonthly = dict(
                (k.id, json.dumps({"series": [v2 for k2, v2 in v.items()]}))
                for k, v in drilldown[0].items()
            )
            dyearly = dict(
                (k.id, json.dumps({"series": [v2 for k2, v2 in v.items()]}))
                for k, v in drilldown[1].items()
            )

        context["series_monthly"] = monthly
        context["series_yearly"] = yearly
        context["drilldown_monthly"] = dmonthly
        context["drilldown_yearly"] = dyearly
        return context

    def get_object(self, queryset=None):
        """Get object."""
        if Budget.objects.count() == 0:
            Budget.objects.create()
        return Budget.objects.first()

    def series(self, name: str, unit: Unit) -> Dict:
        """Series."""
        return {
            "name": str(name),
            "colorByPoint": True,
            "dataLabels": {
                "enabled": True,
                "format": "{point.name}: {point.v:.%df} %s"
                % (unit.precision, unit.symbol),
            },
            "tooltip": {
                "headerFormat": '<span style="font-size:11px">'
                + "{series.name}</span><br>",
                "pointFormat": (
                    '<span style="color:{point.color}">'
                    + "{point.name}</span>: <b>{point.v:.%df} %s"
                    + "</b><br/>"
                )
                % (unit.precision, unit.symbol),
            },
            "data": [],
        }

    def drilldown(self, name: str, id: str, unit: Unit) -> Dict:
        """Drilldown."""
        return {
            "name": str(name),
            "id": id,
            "dataLabels": {
                "enabled": True,
                "format": "{point.name}: {point.v:.%df} %s"
                % (unit.precision, unit.symbol),
            },
            "tooltip": {
                "headerFormat": '<span style="font-size:11px">'
                + "{series.name}</span><br>",
                "pointFormat": (
                    '<span style="color:{point.color}">'
                    + "{point.name}</span>: <b>{point.v:.%df} %s"
                    + "</b><br/>"
                )
                % (unit.precision, unit.symbol),
            },
            "data": [],
        }

    def calculate_part(
        self,
        tags,
        year: int,
        key: str,
        name: str,
        entry_ids: Set[int],
        series: Tuple[Dict, Dict],
        drilldown: Tuple[Dict, Dict],
        footer,
        footer_idx: int,
        units,
    ) -> List:
        """Calculate everything for a part of the budget."""
        part = []
        for tag in tags:
            amounts: Dict[Unit, float] = {}
            for e in Entry.objects.filter(
                Q(date__year=year) & Q(tags__pk=tag.pk)
            ).annotate(total=F("amount") + F("fees")):
                if e.pk not in entry_ids:
                    entry_ids.add(e.pk)
                    if e.account.unit in amounts:
                        amounts[e.account.unit] += e.total
                    else:
                        amounts[e.account.unit] = e.total

            for i, (unit, v) in enumerate(amounts.items()):
                part.append(
                    {
                        "pk": tag.pk if i < 1 else "",
                        "name": tag.name if i < 1 else "",
                        "monthly": unitcolorfy(v / 12, unit),
                        "yearly": unitcolorfy(v, unit),
                    }
                )
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if key not in drilldown[0][unit]:
                    drilldown[0][unit][key] = self.drilldown(name, key, unit)
                    drilldown[1][unit][key] = self.drilldown(name, key, unit)
                drilldown[0][unit][key]["data"].append(
                    {
                        "name": tag.name,
                        "v": v / 12,
                        "y": abs(v) / 12,
                        "drilldown": f"{key}_{tag.pk}",
                    }
                )
                drilldown[1][unit][key]["data"].append(
                    {
                        "name": tag.name,
                        "v": v,
                        "y": abs(v),
                        "drilldown": f"{key}_{tag.pk}",
                    }
                )
                drilldown[0][unit][tag.pk] = self.drilldown(
                    tag.name, f"{key}_{tag.pk}", unit
                )
                drilldown[1][unit][tag.pk] = self.drilldown(
                    tag.name, f"{key}_{tag.pk}", unit
                )
                categories: Tuple[Dict[Any, Any], Dict[Any, Any]] = (
                    {},
                    {},
                )
                for e in Entry.objects.filter(
                    Q(date__year=year) & Q(account__unit=unit) & Q(tags=tag)
                ).annotate(total=F("amount") + F("fees")):
                    if e.category.pk in categories[0]:
                        categories[0][e.category.pk]["v"] += e.total / 12
                        categories[1][e.category.pk]["v"] += e.total
                    else:
                        categories[0][e.category.pk] = {
                            "name": e.category.name,
                            "v": e.total / 12,
                        }
                        categories[1][e.category.pk] = {
                            "name": e.category.name,
                            "v": e.total,
                        }
                for k in categories[0].keys():
                    categories[0][k]["y"] = abs(categories[0][k]["v"])
                    categories[1][k]["y"] = abs(categories[1][k]["v"])
                drilldown[0][unit][tag.pk]["data"] = [
                    v for k, v in categories[0].items()
                ]
                drilldown[1][unit][tag.pk]["data"] = [
                    v for k, v in categories[1].items()
                ]
            for k, v in amounts.items():
                if k in footer[footer_idx]:
                    footer[footer_idx][k] += v / 12
                else:
                    footer[footer_idx][k] = v / 12
                if k in footer[footer_idx + 1]:
                    footer[footer_idx + 1][k] += v
                else:
                    footer[footer_idx + 1][k] = v
        units.update(footer[footer_idx].keys())
        for unit in units:
            if unit not in series[0] and unit not in series[1]:
                series[0][unit] = self.series(
                    _("Budget %(unit)s" % {"unit": unit.name})
                    if len(units) > 1
                    else _("Budget"),
                    unit,
                )
                series[1][unit] = self.series(
                    _("Budget %(unit)s" % {"unit": unit.name})
                    if len(units) > 1
                    else _("Budget"),
                    unit,
                )
            series[0][unit]["data"].append(
                {
                    "name": str(name),
                    "v": footer[footer_idx + 1][unit] / 12,
                    "y": abs(footer[footer_idx + 1][unit]) / 12,
                    "drilldown": key,
                }
            )
            series[1][unit]["data"].append(
                {
                    "name": str(name),
                    "v": footer[footer_idx + 1][unit],
                    "y": abs(footer[footer_idx + 1][unit]),
                    "drilldown": key,
                }
            )

        return part


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """Budget update view."""

    form_class = BudgetForm
    model = Budget
    success_message = _("Your budget was successfully updated.")

    def get_object(self, queryset=None):
        """Get object."""
        return Budget.objects.first()

    def get_success_url(self):
        """Get success URL."""
        url = reverse_lazy("create_another_success")
        if "reload" in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        return url
