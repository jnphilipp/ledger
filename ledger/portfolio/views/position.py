# Copyright (C) 2014-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Portfolio Django app position views."""

import json

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Min, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic
from ledger.dates import daterange

from ..forms import PositionFilterForm, PositionForm
from ..models import ETF, Fund, Position, Stock, Trade


def autocomplete(request):
    """Handels GET/POST request to autocomplete positions.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    positions = Position.objects.annotate(Count("trades")).order_by(
        "closed", "-trades__count"
    )
    q = None
    if "q" in params:
        q = params.pop("q")[0]
        positions = positions.filter(
            Q(portfolio_etfs__name__icontains=q)
            | Q(portfolio_etfs__isin__icontains=q)
            | Q(portfolio_etfs__wkn__icontains=q)
            | Q(portfolio_etfs__symbol__icontains=q)
            | Q(portfolio_funds__name__icontains=q)
            | Q(portfolio_funds__isin__icontains=q)
            | Q(portfolio_funds__wkn__icontains=q)
            | Q(portfolio_funds__symbol__icontains=q)
            | Q(portfolio_stocks__name__icontains=q)
            | Q(portfolio_stocks__isin__icontains=q)
            | Q(portfolio_stocks__wkn__icontains=q)
            | Q(portfolio_stocks__symbol__icontains=q)
        )

    return JsonResponse(
        {
            "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
            "positions": [
                {"id": position.id, "text": str(position)} for position in positions
            ],
        }
    )


def chart(request, slug):
    """GET JSON data for highchart position graph."""
    position = get_object_or_404(Position, slug=slug)

    units = 0
    costs = 0
    last = None

    spread_data = []
    closing_data = []
    win_loss_data = []
    for trading_date in daterange(position.start_date(), position.end_date(), "days"):
        for trade in position.trades.filter(date=trading_date):
            if (
                trade.type == Trade.TradeType.BUY
                or trade.type == Trade.TradeType.CORPORATE_ACTION
            ):
                units = round(units + trade.units, 6)
                costs += trade.total()
            elif trade.type == Trade.TradeType.SELL:
                units = round(units - trade.units, 6)
                costs -= trade.total()
            elif trade.type == Trade.TradeType.DIVIDEND:
                costs -= trade.total()

        last = win_loss = (
            round((costs if costs >= 0.0 else 0) / units, position.unit.precision)
            if units != 0
            else last
        )

        if position.content_object.closings.filter(date=trading_date).exists():
            closing = position.content_object.closings.get(date=trading_date)
            closing_data.append([trading_date.strftime("%Y-%m-%d"), closing.price])
            spread_data.append(
                [
                    trading_date.strftime("%Y-%m-%d"),
                    closing.low,
                    closing.high,
                ]
            )
            win_loss_data.append([trading_date.strftime("%Y-%m-%d"), win_loss])
        elif position.trades.filter(date=trading_date).exists():
            win_loss_data.append([trading_date.strftime("%Y-%m-%d"), win_loss])
    if units != 0:
        win_loss_data.append([position.end_date().strftime("%Y-%m-%d"), last])

    series = []
    if closing_data and spread_data:
        series.append(
            {
                "data": closing_data,
                "name": str(position.content_object),
                "tooltip": {"valueSuffix": position.content_object.currency.symbol},
            }
        )
        series.append(
            {
                "data": spread_data,
                "fillOpacity": 0.3,
                "linkedTo": ":previous",
                "lineWidth": 0,
                "name": _("Spread"),
                "tooltip": {"valueSuffix": position.content_object.currency.symbol},
                "type": "arearange",
                "zIndex": 0,
                "marker": {"enabled": False},
            }
        )
    if win_loss_data:
        series.append(
            {
                "name": _("Win/Loss Limit"),
                "data": win_loss_data,
                "tooltip": {"valueSuffix": position.unit.symbol},
                "step": "left",
            }
        )
    data = {
        "series": series,
        "yAxis": {"title": _("Price"), "unit": "{value}%s" % position.unit.symbol},
    }
    return JsonResponse(data)


class ListView(generic.ListView):
    """Position list view."""

    context_object_name = "positions"
    model = Position
    ordering = ["closed", "-slug"]
    paginate_by = 200

    def get_queryset(self):
        """Get queryset."""
        positions = super().get_queryset()

        self.closed = None
        self.tradeables = []
        self.form = PositionFilterForm(self.request.GET)
        if self.form.is_valid():
            if self.form.cleaned_data["closed"]:
                self.closed = self.form.cleaned_data["closed"]
                if self.closed != "0":
                    positions = positions.filter(
                        closed=self.form.cleaned_data["closed"]
                    )
            if self.form.cleaned_data["tradeables"]:
                self.tradeables = self.form.cleaned_data["tradeables"]
                funds = []
                etfs = []
                stocks = []
                for t in self.form.cleaned_data["tradeables"]:
                    if t.startswith("etf:"):
                        etfs.append(t.replace("etf:", ""))
                    elif t.startswith("fund:"):
                        funds.append(t.replace("fund:", ""))
                    if t.startswith("stock:"):
                        stocks.append(t.replace("stock:", ""))
                if funds:
                    positions = positions.filter(portfolio_funds__in=funds)
                if etfs:
                    positions = positions.filter(portfolio_etfs__in=etfs)
                if stocks:
                    positions = positions.filter(portfolio_stocks__in=stocks)
        return positions.annotate(Min("trades__date")).order_by(
            "closed", "-trades__date__min"
        )

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(*args, **kwargs)

        context["has_tradeables"] = (
            ETF.objects.count() > 0
            or Fund.objects.count() > 0
            or Stock.objects.count() > 0
        )

        context["form"] = self.form
        context["closed"] = self.closed
        context["tradeables"] = self.tradeables

        return context


class DetailView(generic.DetailView):
    """Position detail view."""

    model = Position


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """Position create view."""

    form_class = PositionForm
    model = Position
    success_message = _('The position "%(name)s" was successfully created.')
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {"name": self.object.slug}


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """Position update view."""

    form_class = PositionForm
    model = Position
    success_url = reverse_lazy("create_another_success")

    def get_initial(self):
        """Get initial."""
        return {
            "tradeable": f"{self.object.content_type.model.lower()}:"
            + f"{self.object.content_object.pk}",
        }

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The position "%(name)s" was successfully updated.') % {
            "name": self.object
        }


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    """Position delete view."""

    model = Position

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The position "%(name)s" was successfully deleted.') % {
            "name": self.object.slug
        }

    def get_success_url(self):
        """Get success URL."""
        return (
            f"{reverse_lazy('create_another_success')}?next="
            + f"{reverse_lazy('portfolio:position_list')}"
        )


class CloseView(generic.base.RedirectView):
    """Position close view."""

    def get_redirect_url(self, *args, **kwargs):
        """Get redirect URL."""
        position = get_object_or_404(Position, slug=kwargs["slug"])
        position.closed = not position.closed
        position.save()

        if position.closed:
            msg = _('The position "%(name)s" was successfully closed.')
        else:
            msg = _('The position "%(name)s" was successfully re-open.')

        msg %= {"name": position.slug}
        messages.add_message(self.request, messages.SUCCESS, msg)
        return reverse_lazy("portfolio:position_list")
