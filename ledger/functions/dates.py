# -*- coding: utf-8 -*-

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
        if c == end:
            break;
        c = start + relativedelta(months=+i)
        dates.append(c)
    return dates


def days_in_month(month):
    """https://cmcenroe.me/2014/12/05/days-in-month-formula.html"""
    return 28 + (month + floor(month / 8)) % 2 + 2 % month + 2 * floor(1 / month)


def get_last_date_current_month():
    today = date.today()
    return date(year=today.year, month=today.month, day=monthrange(today.year, today.month)[1])
