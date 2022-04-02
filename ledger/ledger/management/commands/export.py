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
"""Ledger Django app export command."""

import json
import sys

from argparse import FileType
from django.core.management.base import BaseCommand
from portfolio.models import ETF, Fund, Position, Stock

from ...models import Account, Budget


class Command(BaseCommand):
    """Export command."""

    help = "Export everything to json."

    def add_arguments(self, parser):
        """Add arguments for parser."""
        parser.add_argument("-r", "--renumber", action="store_true")
        parser.add_argument(
            "output", nargs="?", type=FileType("w", encoding="utf8"), default=sys.stdout
        )

    def handle(self, *args, **options):
        """Handle command."""
        data = {"accounts": [], "portfolio": [], "tradeables": []}
        for account in Account.objects.all():
            if options["renumber"]:
                account.renumber_entries()
            data["accounts"].append(
                {
                    "name": account.name,
                    "category": account.category.name,
                    "closed": account.closed,
                    "unit": {
                        "name": account.unit.name,
                        "code": account.unit.code,
                        "symbol": account.unit.symbol,
                        "precision": account.unit.precision,
                    },
                    "files": [
                        {"name": file.name, "file": file.file.path}
                        for file in account.files.all()
                    ],
                    "entries": [
                        {
                            "serial_number": entry.serial_number,
                            "date": entry.date.strftime("%Y-%m-%d"),
                            "amount": entry.amount,
                            "fees": entry.fees,
                            "category": entry.category.name,
                            "text": entry.text if entry.text else None,
                            "tags": [tag.name for tag in entry.tags.all()],
                            "files": [
                                {"name": file.name, "file": file.file.path}
                                for file in entry.files.all()
                            ],
                        }
                        for entry in account.entries.all()
                    ],
                }
            )

        budget = Budget.objects.first()
        data["budget"] = {
            "income_tags": [tag.name for tag in budget.income_tags.all()],
            "consumption_tags": [tag.name for tag in budget.consumption_tags.all()],
            "insurance_tags": [tag.name for tag in budget.insurance_tags.all()],
            "savings_tags": [tag.name for tag in budget.savings_tags.all()],
        }

        for position in Position.objects.all():
            if options["renumber"]:
                position.renumber_trades()
            data["portfolio"].append(
                {
                    "slug": position.slug,
                    "closed": position.closed,
                    "trailing_stop_atr_factor": position.trailing_stop_atr_factor,
                    "unit": {
                        "name": position.unit.name,
                        "code": position.unit.code,
                        "symbol": position.unit.symbol,
                        "precision": position.unit.precision,
                    },
                    "tradeable": {
                        "name": position.content_object.name,
                        "isin": position.content_object.isin,
                        "wkn": position.content_object.wkn,
                        "symbol": position.content_object.symbol,
                        "traded": position.content_object.traded,
                        "type": position.content_object.__class__.__name__.lower(),
                        "currency": {
                            "name": position.content_object.currency.name,
                            "code": position.content_object.currency.code,
                            "symbol": position.content_object.currency.symbol,
                            "precision": position.content_object.currency.precision,
                        },
                    },
                    "trades": [
                        {
                            "serial_number": trade.serial_number,
                            "type": trade.type,
                            "date": trade.date.strftime("%Y-%m-%d"),
                            "units": trade.units,
                            "unit_price": trade.unit_price,
                            "extra": trade.extra,
                            "extra2": trade.extra2,
                            "exchange_rate": trade.exchange_rate,
                            "unit": {
                                "name": trade.unit.name,
                                "code": trade.unit.code,
                                "symbol": trade.unit.symbol,
                                "precision": trade.unit.precision,
                            },
                        }
                        for trade in position.trades.all().reverse()
                    ],
                }
            )

        for tradeable in (
            list(ETF.objects.all())
            + list(Fund.objects.all())
            + list(Stock.objects.all())
        ):
            if tradeable.closings.count() == 0:
                continue

            data["tradeables"].append(
                {
                    "name": tradeable.name,
                    "isin": tradeable.isin,
                    "wkn": tradeable.wkn,
                    "symbol": tradeable.symbol,
                    "traded": tradeable.traded,
                    "type": tradeable.__class__.__name__.lower(),
                    "currency": {
                        "name": tradeable.currency.name,
                        "code": tradeable.currency.code,
                        "symbol": tradeable.currency.symbol,
                        "precision": tradeable.currency.precision,
                    },
                    "closings": [
                        {
                            "date": closing.date.strftime("%Y-%m-%d"),
                            "price": closing.price,
                            "high": closing.high,
                            "low": closing.low,
                            "change_previous": closing.change_previous,
                            "change_previous_percent": closing.change_previous_percent,
                        }
                        for closing in tradeable.closings.all().reverse()
                    ],
                }
            )

        options["output"].write(json.dumps(data, indent=4, ensure_ascii=False))
        options["output"].write("\n")
