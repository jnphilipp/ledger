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
"""Ledger Django units templatetags."""

from django.template import Library
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe
from typing import Optional, Union

from ..models import Unit


register = Library()


@register.filter
def unitformat(amount: Optional[float], unit: Optional[Union[str, Unit]] = None) -> str:
    """Colorfy template filter."""
    if amount is None:
        return ""
    if isinstance(unit, Unit):
        precision = unit.precision if unit else 2
        symbol = unit.symbol if unit else ""
        return mark_safe(
            f"{floatformat(amount if amount else 0., precision)} {symbol}".strip()
        )
    elif isinstance(unit, str):
        return mark_safe(unit % amount)
    else:
        return f"{amount}"


@register.filter
def unitcolorfy(
    amount: Optional[float], unit: Optional[Union[str, Unit]] = None
) -> str:
    """Colorfy template filter."""
    if amount is None:
        return ""
    if isinstance(unit, Unit):
        precision = unit.precision if unit else 2
        symbol = unit.symbol if unit else ""
        if amount == 0.0:
            return unitformat(amount, unit)
        else:
            return mark_safe(
                f'<span class="{"green" if amount >=0. else "red"}"'
                + f">{floatformat(amount, precision)} {symbol}</span>"
            )
    elif isinstance(unit, str):
        if amount == 0.0:
            return unitformat(amount, unit)
        else:
            return mark_safe(
                f'<span class="{"green" if amount > 0. else "red"}"'
                + f">{unit % amount}</span>"
            )
    else:
        return f"{amount}"
