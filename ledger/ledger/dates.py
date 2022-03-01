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

from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta
from itertools import count
from math import floor


def daterange(start, end, execution=1):
    if execution == 1:
        step = 1
    elif execution == 2:
        step = 3
    elif execution == 3:
        step = 6
    elif execution == 4:
        step = 12
    else:
        step = execution

    c = start
    dates = []
    for i in count(step=step):
        c = start + relativedelta(months=+i)
        if c > end:
            break
        dates.append(c)
    return dates


def days_in_month(month):
    """https://cmcenroe.me/2014/12/05/days-in-month-formula.html"""
    return 28 + (month + floor(month / 8)) % 2 + 2 % month + 2 * floor(1 / month)


def get_last_date_current_month():
    today = date.today()
    return date(
        year=today.year, month=today.month, day=monthrange(today.year, today.month)[1]
    )
