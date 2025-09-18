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
"""Portfolio Django app portfolio templatetags."""

from django.db.models import Q, QuerySet, Sum
from django.db.models.functions import Coalesce
from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from units.templatetags.units import unitcolorfy, unitformat

from ..models import Position, Trade, Tradeable


register = Library()


@register.filter
def as_title(tradeable: Tradeable) -> str:
    """Format tradeable information as tooltip title template filter."""
    return mark_safe(
        f"{_('Name')}: {tradeable.name}<br>"
        + (f"{_('ISIN')}: {tradeable.isin}<br>" if tradeable.isin else "")
        + (f"{_('WKN')}: {tradeable.wkn}<br>" if tradeable.wkn else "")
        + (f"{_('Symbol')}: {tradeable.symbol}<br>" if tradeable.symbol else "")
        + (f"{_('Currency')}: {tradeable.currency}<br>" if tradeable.currency else "")
        + f"{_('Traded')}: {_('yes') if tradeable.traded else _('no')}<br>"
    )


@register.filter
def duration(position: QuerySet[Position]) -> str:
    """Position duration template filter."""
    return ngettext_lazy("%(days)d day", "%(days)d days", "days") % {
        "days": (position.end_date() - position.start_date()).days
    }


@register.simple_tag
def invested(positions: QuerySet[Position]) -> str:
    """Sum of positions invested simple template tag."""
    sums = {}
    for position in positions:
        if position.trades.count() == 0:
            continue
        if position.unit not in sums:
            sums[position.unit] = 0.0
        sums[position.unit] += position.invested()
    return mark_safe("<br>".join([unitformat(v, k) for k, v in sums.items()]))


@register.simple_tag
def win_loss(positions: QuerySet[Position]) -> str:
    """Sum of positions win/loss simple template tag."""
    sums = {}
    for position in positions:
        if position.trades.count() == 0:
            continue
        if position.unit not in sums:
            sums[position.unit] = 0.0
        sums[position.unit] += position.win_loss()
    return mark_safe("<br>".join([unitcolorfy(v, k) for k, v in sums.items()]))


@register.simple_tag
def dividend(positions: QuerySet[Position]) -> str:
    """Sum of positions dividend simple template tag."""
    sums = {}
    for position in positions:
        if position.trades.count() == 0:
            continue
        if position.unit not in sums:
            sums[position.unit] = 0.0
        sums[position.unit] += position.dividend()
    return mark_safe("<br>".join([unitformat(v, k) for k, v in sums.items()]))


@register.simple_tag
def annual_return(positions: QuerySet[Position]) -> str:
    """Annual return of positions simple template tag."""
    trades = Trade.objects.filter(position__in=positions).order_by("-serial_number")
    if trades.count() == 0:
        return mark_safe("")

    total_costs = 0.0
    total_gain = 0.0
    time = 0
    for position in positions:
        costs = sum(
            [
                trade.total()
                for trade in position.trades.filter(
                    Q(type=Trade.TradeType.BUY)
                    | Q(type=Trade.TradeType.PRE_EMPTION_RIGHT)
                    | Q(type=Trade.TradeType.CORPORATE_ACTION)
                )
            ]
        )
        bought = position.trades.filter(
            Q(type=Trade.TradeType.BUY) | Q(type=Trade.TradeType.CORPORATE_ACTION)
        ).aggregate(units=Coalesce(Sum("units"), 0.0))["units"]
        gain = sum(
            [
                trade.total()
                for trade in position.trades.filter(type=Trade.TradeType.SELL)
            ]
        )
        sold = position.trades.filter(type=Trade.TradeType.SELL).aggregate(
            units=Coalesce(Sum("units"), 0.0)
        )["units"]

        if position.content_object.closings.count() == 0 and not position.closed:
            gain += position.trades.filter(
                Q(type=Trade.TradeType.BUY) | Q(type=Trade.TradeType.SELL)
            ).first().unit_price * (bought - sold)
        elif not position.closed:
            gain += position.content_object.closings.first().price * (bought - sold)

        total_costs += costs
        total_gain += gain
        time = max(time, position.duration())
    return mark_safe(
        unitcolorfy(
            (
                (pow(total_gain / total_costs, 365 / time) - 1) * 100
                if time > 0 and total_costs > 0
                else 0.0
            ),
            "%.3f%%",
        )
    )
