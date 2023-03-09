# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2023 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Portfolio Django app tradeable views."""

import json

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..forms import TradeableForm
from ..models import ETF, Fund, Stock, Tradeable


def autocomplete(request):
    """Handels GET/POST request to autocomplete tradeables.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    etfs = ETF.objects.annotate(Count("positions")).order_by("-positions__count")
    funds = Fund.objects.annotate(Count("positions")).order_by("-positions__count")
    stocks = Stock.objects.annotate(Count("positions")).order_by("-positions__count")
    q = None
    if "q" in params:
        q = params.pop("q")[0]
        etfs = etfs.filter(
            Q(name__icontains=q)
            | Q(isin__icontains=q)
            | Q(wkn__icontains=q)
            | Q(symbol__icontains=q)
        )
        stocks = stocks.filter(
            Q(name__icontains=q)
            | Q(isin__icontains=q)
            | Q(wkn__icontains=q)
            | Q(symbol__icontains=q)
        )
        funds = funds.filter(
            Q(name__icontains=q)
            | Q(isin__icontains=q)
            | Q(wkn__icontains=q)
            | Q(symbol__icontains=q)
        )

    data = {
        "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
        "tradeables": sorted(
            [
                {"id": f"etf:{etf.pk}", "text": etf.name, "count": etf.positions__count}
                for etf in etfs
            ]
            + [
                {
                    "id": f"fund:{fund.pk}",
                    "text": fund.name,
                    "count": fund.positions__count,
                }
                for fund in funds
            ]
            + [
                {
                    "id": f"stock:{stock.pk}",
                    "text": stock.name,
                    "count": stock.positions__count,
                }
                for stock in stocks
            ],
            key=lambda x: x["count"],
        ),
    }
    return JsonResponse(data)


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """Tradeable create view."""

    form_class = TradeableForm
    model = Tradeable
    success_message = _('The tradeable (%(type)s) "%(name)s" was successfully created.')
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        print(self.object)
        return self.success_message % {
            "type": self.object._meta.verbose_name.title(),
            "name": self.object.name,
        }


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """Tradeable update view."""

    form_class = TradeableForm
    model = Tradeable
    success_message = _('The tradeable (%(type)s) "%(name)s" was successfully update.')
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {"name": self.object.name}


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    """Tradeable delete view."""

    form_class = TradeableForm
    model = Tradeable
    success_message = _('The tradeable (%(type)s) "%(name)s" was successfully deleted.')
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {"name": self.object.name}
