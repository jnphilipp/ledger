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

from django.test import TestCase
from units.models import Unit

from ..models import ETF, Position, Trade


class TradeModelTestCase(TestCase):
    def setUp(self):
        etf = ETF.objects.create(name="Test ETF")
        self.etf_position = Position.objects.create(
            content_object=etf, closed=True, unit=Unit.objects.get(code="EUR")
        )

    def test_total(self):
        trade = Trade.objects.create(
            date="2022-01-01",
            units=100,
            unit_price=10,
            extra=4,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.BUY,
            position=self.etf_position,
        )
        self.assertEqual(trade.total(), 1004.0)

        trade = Trade.objects.create(
            date="2022-02-15",
            units=100,
            unit_price=3,
            extra=0.0,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.PRE_EMPTION_RIGHT,
            position=self.etf_position,
        )
        self.assertEqual(trade.total(), 300.0)

        trade = Trade.objects.create(
            date="2022-02-01",
            units=100,
            unit_price=1,
            extra=4,
            unit=Unit.objects.get(code="USD"),
            type=Trade.TradeType.DIVIDEND,
            position=self.etf_position,
        )
        self.assertEqual(trade.total(), 96.0)

        trade = Trade.objects.create(
            date="2022-02-01",
            units=100,
            unit_price=1,
            extra=4,
            extra2=5,
            exchange_rate=1.12345,
            unit=Unit.objects.get(code="USD"),
            type=Trade.TradeType.DIVIDEND,
            position=self.etf_position,
        )
        self.assertEqual(trade.total(), 80.45)

        trade = Trade.objects.create(
            date="2022-02-20",
            units=100,
            unit_price=15,
            extra=6,
            unit=Unit.objects.get(code="EUR"),
            type=Trade.TradeType.SELL,
            position=self.etf_position,
        )
        self.assertEqual(trade.total(), 1494.0)
