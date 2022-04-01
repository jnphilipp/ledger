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
"""Portfolio Django app portfolio templatetags."""

from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, ngettext_lazy

from units.templatetags.units import unitcolorfy


register = Library()


@register.filter
def as_title(tradeable):
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
def duration(position):
    """Position duration template filter."""
    return ngettext_lazy("%(days)d day", "%(days)d days", "days") % {
        "days": (position.end_date() - position.start_date()).days
    }


@register.simple_tag
def invested(positions) -> float:
    """Sum of positions invested simple template tag."""
    sums = {}
    for position in positions:
        if position.trades.count() == 0:
            continue
        if position.unit not in sums:
            sums[position.unit] = 0.0
        sums[position.unit] += position.invested()
    return mark_safe("<br>".join([unitcolorfy(v, k) for k, v in sums.items()]))


@register.simple_tag
def win_loss(positions) -> float:
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
def dividend(positions) -> float:
    """Sum of positions dividend simple template tag."""
    sums = {}
    for position in positions:
        if position.trades.count() == 0:
            continue
        if position.unit not in sums:
            sums[position.unit] = 0.0
        sums[position.unit] += position.dividend()
    return mark_safe("<br>".join([unitcolorfy(v, k) for k, v in sums.items()]))
