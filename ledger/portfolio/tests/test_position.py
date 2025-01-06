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

        stock = Stock.objects.create(name="Other stock")
        self.stock_position2 = Position.objects.create(
            content_object=stock, unit=Unit.objects.get(code="EUR")
        )
        Trade.objects.create(
            date="2021-06-20",
            units=50,
            unit_price=23,
            extra=8,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.stock_position2,
        )
        Trade.objects.create(
            date="2021-12-15",
            units=50,
            unit_price=30,
            extra=10,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.stock_position2,
        )
        Trade.objects.create(
            date="2022-01-19",
            units=100,
            unit_price=7,
            extra=0,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.PRE_EMPTION_RIGHT,
            position=self.stock_position2,
        )
        Trade.objects.create(
            date="2022-03-21",
            units=30,
            unit_price=18,
            extra=5,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.stock_position2,
        )

    def test_start_date(self):
        self.assertEqual(
            self.etf_position.start_date(), date(year=2022, month=1, day=1)
        )
        self.assertEqual(
            self.fund_position.start_date(), date(year=2022, month=1, day=1)
        )
        self.assertEqual(
            self.stock_position.start_date(), date(year=2020, month=5, day=10)
        )
        self.assertEqual(
            self.stock_position2.start_date(), date(year=2021, month=6, day=20)
        )

    def test_end_date(self):
        self.assertEqual(self.etf_position.end_date(), date(year=2022, month=1, day=31))
        self.assertEqual(self.fund_position.end_date(), timezone.now().date())
        self.assertEqual(self.stock_position.end_date(), timezone.now().date())
        self.assertEqual(self.stock_position2.end_date(), timezone.now().date())

    def test_annual_return(self):
        with patch.object(timezone, "now", new=lambda: datetime(2022, 3, 31)):
            self.assertEqual(self.etf_position.annual_return(), 411952.21888563794)
            self.assertEqual(self.fund_position.annual_return(), 23.412243666891207)
            self.assertEqual(self.stock_position.annual_return(), 29.632379989801816)
            self.assertEqual(self.stock_position2.annual_return(), -48.355979192289425)

    def test_dividend(self):
        self.assertEqual(self.etf_position.dividend(), 0.0)
        self.assertEqual(self.fund_position.dividend(), 26.0)
        self.assertEqual(self.stock_position.dividend(), 99.0)
        self.assertEqual(self.stock_position2.dividend(), 0.0)

    def test_duration(self):
        with patch.object(timezone, "now", new=lambda: datetime(2022, 3, 31)):
            self.assertEqual(self.etf_position.duration(), 30.0)
            self.assertEqual(self.fund_position.duration(), 89)
            self.assertEqual(
                self.stock_position.duration(),
                690,
            )
            self.assertEqual(
                self.stock_position2.duration(),
                284,
            )

    def test_invested(self):
        self.assertEqual(self.etf_position.invested(), 0.0)
        self.assertEqual(self.fund_position.invested(), 342.0)
        self.assertEqual(self.stock_position.invested(), 60.0)
        self.assertEqual(self.stock_position2.invested(), 3913.0)

    def test_preturn(self):
        self.assertEqual(self.etf_position.preturn(), 1990.0)
        self.assertEqual(self.fund_position.preturn(), 360.0)
        self.assertEqual(self.stock_position.preturn(), 490.0)
        self.assertEqual(self.stock_position2.preturn(), 2340.0)

    def test_units(self):
        self.assertEqual(self.etf_position.units(), 0.0)
        self.assertEqual(self.fund_position.units(), 30.0)
        self.assertEqual(self.stock_position.units(), 25.0)
        self.assertEqual(self.stock_position2.units(), 130.0)

    def test_win_loss(self):
        self.assertEqual(self.etf_position.win_loss(), 986.0)
        self.assertEqual(self.fund_position.win_loss(), 18.0)
        self.assertEqual(self.stock_position.win_loss(), 190.0)
        self.assertEqual(self.stock_position2.win_loss(), -1573.0)
