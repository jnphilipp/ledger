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

from datetime import date, datetime
from django.test import TestCase
from django.utils import timezone
from units.models import Unit
from unittest.mock import patch

from ..models import ETF, Fund, Position, Stock, Trade


class PositionModelTestCase(TestCase):
    def setUp(self):
        etf = ETF.objects.create(name="Test ETF")
        self.etf_position = Position.objects.create(
            content_object=etf, closed=True, unit=Unit.objects.get(code="EUR")
        )
        Trade.objects.create(
            date="2022-01-01",
            units=100,
            unit_price=10,
            extra=4,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.etf_position,
        )
        Trade.objects.create(
            date="2022-01-31",
            units=100,
            unit_price=20,
            extra=10,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.SELL,
            position=self.etf_position,
        )

        fund = Fund.objects.create(name="Test fund")
        self.fund_position = Position.objects.create(
            content_object=fund, unit=Unit.objects.get(code="EUR")
        )
        Trade.objects.create(
            date="2022-01-01",
            units=10,
            unit_price=10,
            extra=4,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.fund_position,
        )
        Trade.objects.create(
            date="2022-02-01",
            units=10,
            unit_price=11,
            extra=4,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.fund_position,
        )
        Trade.objects.create(
            date="2022-03-01",
            units=10,
            unit_price=12,
            extra=4,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.fund_position,
        )
        Trade.objects.create(
            date="2022-03-15",
            units=30,
            unit_price=1,
            extra=4,
            unit=Unit.objects.get(code="USD"),
            type=Trade.TradeType.DIVIDEND,
            position=self.fund_position,
        )

        stock = Stock.objects.create(name="Test stock")
        self.stock_position = Position.objects.create(
            content_object=stock, unit=Unit.objects.get(code="EUR")
        )
        Trade.objects.create(
            date="2020-05-10",
            units=30,
            unit_price=5,
            extra=5,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.stock_position,
        )
        Trade.objects.create(
            date="2020-06-15",
            units=30,
            unit_price=1,
            extra=3,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.DIVIDEND,
            position=self.stock_position,
        )
        Trade.objects.create(
            date="2021-04-19",
            units=20,
            unit_price=7,
            extra=5,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.stock_position,
        )
        Trade.objects.create(
            date="2021-06-21",
            units=50,
            unit_price=1.5,
            extra=3,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.DIVIDEND,
            position=self.stock_position,
        )
        Trade.objects.create(
            date="2022-01-13",
            units=25,
            unit_price=10,
            extra=10,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.SELL,
            position=self.stock_position,
        )

    def test_start_date(self):
        self.assertEquals(
            self.etf_position.start_date(), date(year=2022, month=1, day=1)
        )
        self.assertEquals(
            self.fund_position.start_date(), date(year=2022, month=1, day=1)
        )
        self.assertEquals(
            self.stock_position.start_date(), date(year=2020, month=5, day=10)
        )

    def test_end_date(self):
        self.assertEquals(
            self.etf_position.end_date(), date(year=2022, month=1, day=31)
        )
        self.assertEquals(self.fund_position.end_date(), timezone.now().date())
        self.assertEquals(self.stock_position.end_date(), timezone.now().date())

    def test_annual_return(self):
        with patch.object(timezone, "now", new=lambda: datetime(2022, 3, 31)):
            self.assertEquals(self.etf_position.annual_return(), 411952.21888563794)
            self.assertEquals(self.fund_position.annual_return(), 23.412243666891207)
            self.assertEquals(self.stock_position.annual_return(), 29.632379989801816)

    def test_dividend(self):
        self.assertEquals(self.etf_position.dividend(), 0.0)
        self.assertEquals(self.fund_position.dividend(), 26.0)
        self.assertEquals(self.stock_position.dividend(), 99.0)

    def test_duration(self):
        self.assertEquals(self.etf_position.duration(), 30.0)
        self.assertEquals(
            self.fund_position.duration(),
            (self.fund_position.end_date() - self.fund_position.start_date()).days,
        )
        self.assertEquals(
            self.stock_position.duration(),
            (self.stock_position.end_date() - self.stock_position.start_date()).days,
        )

    def test_invested(self):
        self.assertEquals(self.etf_position.invested(), 0.0)
        self.assertEquals(self.fund_position.invested(), 342.0)
        self.assertEquals(self.stock_position.invested(), 60.0)

    def test_preturn(self):
        self.assertEquals(self.etf_position.preturn(), 1990.0)
        self.assertEquals(self.fund_position.preturn(), 360.0)
        self.assertEquals(self.stock_position.preturn(), 490.0)

    def test_units(self):
        self.assertEquals(self.etf_position.units(), 0.0)
        self.assertEquals(self.fund_position.units(), 30.0)
        self.assertEquals(self.stock_position.units(), 25.0)

    def test_win_loss(self):
        self.assertEquals(self.etf_position.win_loss(), 986.0)
        self.assertEquals(self.fund_position.win_loss(), 18.0)
        self.assertEquals(self.stock_position.win_loss(), 190.0)
