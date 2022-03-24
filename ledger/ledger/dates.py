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
"""Ledger Django app dates module."""

from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta
from itertools import count
from math import floor
from typing import Iterable


def daterange(
    start: date, end: date, repetition_type: str = "days", execution: int = 1
) -> Iterable[date]:
    """Calculate all dates between start and end date, both included."""
    assert repetition_type in ["days", "months", "years"]

    if execution == 1:
        step = 1
    elif execution == 2:
        step = 2
    elif execution == 3:
        step = 3
    elif execution == 4:
        step = 6
    elif execution == 5:
        step = 12
    else:
        step = execution

    for i in count(step=step):
        if repetition_type == "days":
            date = start + relativedelta(days=+i)
        elif repetition_type == "months":
            date = start + relativedelta(months=+i)
        elif repetition_type == "years":
            date = start + relativedelta(years=+i)
        if date > end:
            break
        yield date


def days_in_month(month: int):
    """Calculate the days in a month.

    Source: https://cmcenroe.me/2014/12/05/days-in-month-formula.html
    """
    assert 1 <= month <= 12
    return 28 + (month + floor(month / 8)) % 2 + 2 % month + 2 * floor(1 / month)


def get_last_date_current_month(ref: date = date.today()):
    """Get the last day of in the month of a reference day."""
    return date(year=ref.year, month=ref.month, day=monthrange(ref.year, ref.month)[1])
