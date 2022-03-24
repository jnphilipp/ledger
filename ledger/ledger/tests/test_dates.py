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
"""Ledger Django app dates tests."""

from datetime import date
from django.test import TestCase
from ledger import dates


class DatesTestCase(TestCase):
    def test_daterange_days(self):
        self.assertEquals(
            [
                date(2022, 1, 10),
                date(2022, 1, 11),
                date(2022, 1, 12),
                date(2022, 1, 13),
                date(2022, 1, 14),
                date(2022, 1, 15),
            ],
            list(dates.daterange(date(2022, 1, 10), date(2022, 1, 15), "days", 1)),
        )
        self.assertEquals(
            [
                date(2022, 1, 2),
                date(2022, 1, 4),
                date(2022, 1, 6),
                date(2022, 1, 8),
                date(2022, 1, 10),
            ],
            list(dates.daterange(date(2022, 1, 2), date(2022, 1, 10), "days", 2)),
        )
        self.assertEquals(
            [
                date(2022, 1, 1),
                date(2022, 1, 4),
                date(2022, 1, 7),
                date(2022, 1, 10),
                date(2022, 1, 13),
                date(2022, 1, 16),
                date(2022, 1, 19),
                date(2022, 1, 22),
                date(2022, 1, 25),
                date(2022, 1, 28),
                date(2022, 1, 31),
            ],
            list(dates.daterange(date(2022, 1, 1), date(2022, 1, 31), "days", 3)),
        )
        self.assertEquals(
            [
                date(2022, 1, 1),
                date(2022, 1, 7),
                date(2022, 1, 13),
                date(2022, 1, 19),
                date(2022, 1, 25),
                date(2022, 1, 31),
            ],
            list(dates.daterange(date(2022, 1, 1), date(2022, 1, 31), "days", 4)),
        )
        self.assertEquals(
            [date(2022, 1, 1), date(2022, 1, 13), date(2022, 1, 25)],
            list(dates.daterange(date(2022, 1, 1), date(2022, 1, 31), "days", 5)),
        )

    def test_daterange_months(self):
        self.assertEquals(
            [
                date(2022, 1, 10),
                date(2022, 2, 10),
                date(2022, 3, 10),
                date(2022, 4, 10),
                date(2022, 5, 10),
            ],
            list(dates.daterange(date(2022, 1, 10), date(2022, 5, 10), "months", 1)),
        )
        self.assertEquals(
            [date(2022, 1, 2), date(2022, 3, 2), date(2022, 5, 2)],
            list(dates.daterange(date(2022, 1, 2), date(2022, 5, 2), "months", 2)),
        )
        self.assertEquals(
            [
                date(2022, 1, 23),
                date(2022, 4, 23),
                date(2022, 7, 23),
                date(2022, 10, 23),
            ],
            list(dates.daterange(date(2022, 1, 23), date(2022, 10, 23), "months", 3)),
        )
        self.assertEquals(
            [date(2022, 1, 30), date(2022, 7, 30)],
            list(dates.daterange(date(2022, 1, 30), date(2022, 10, 30), "months", 4)),
        )
        self.assertEquals(
            [date(2022, 1, 31), date(2023, 1, 31)],
            list(dates.daterange(date(2022, 1, 31), date(2023, 1, 31), "months", 5)),
        )

    def test_daterange_years(self):
        self.assertEquals(
            [
                date(2022, 1, 10),
                date(2023, 1, 10),
                date(2024, 1, 10),
                date(2025, 1, 10),
            ],
            list(dates.daterange(date(2022, 1, 10), date(2025, 1, 10), "years", 1)),
        )
        self.assertEquals(
            [
                date(2022, 1, 2),
                date(2024, 1, 2),
                date(2026, 1, 2),
                date(2028, 1, 2),
                date(2030, 1, 2),
                date(2032, 1, 2),
            ],
            list(dates.daterange(date(2022, 1, 2), date(2032, 5, 2), "years", 2)),
        )
        self.assertEquals(
            [
                date(2022, 1, 23),
                date(2025, 1, 23),
                date(2028, 1, 23),
                date(2031, 1, 23),
            ],
            list(dates.daterange(date(2022, 1, 23), date(2032, 10, 23), "years", 3)),
        )
        self.assertEquals(
            [date(2022, 1, 30), date(2028, 1, 30)],
            list(dates.daterange(date(2022, 1, 30), date(2032, 10, 30), "years", 4)),
        )
        self.assertEquals(
            [date(2022, 1, 31), date(2034, 1, 31)],
            list(dates.daterange(date(2022, 1, 31), date(2042, 1, 31), "years", 5)),
        )

    def test_days_in_month(self):
        self.assertEquals(31, dates.days_in_month(1))
        self.assertEquals(28, dates.days_in_month(2))
        self.assertEquals(31, dates.days_in_month(3))
        self.assertEquals(30, dates.days_in_month(4))
        self.assertEquals(31, dates.days_in_month(5))
        self.assertEquals(30, dates.days_in_month(6))
        self.assertEquals(31, dates.days_in_month(7))
        self.assertEquals(31, dates.days_in_month(8))
        self.assertEquals(30, dates.days_in_month(9))
        self.assertEquals(31, dates.days_in_month(10))
        self.assertEquals(30, dates.days_in_month(11))
        self.assertEquals(31, dates.days_in_month(12))

        with self.assertRaises(AssertionError):
            self.assertEquals(31, dates.days_in_month(0))
            self.assertEquals(31, dates.days_in_month(13))

    def test_get_last_date_current_month(self):
        self.assertEquals(
            date(2022, 1, 31), dates.get_last_date_current_month(date(2022, 1, 13))
        )
        self.assertEquals(
            date(2022, 2, 28), dates.get_last_date_current_month(date(2022, 2, 1))
        )
        self.assertEquals(
            date(2020, 2, 29), dates.get_last_date_current_month(date(2020, 2, 1))
        )
