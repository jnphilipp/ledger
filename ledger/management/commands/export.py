# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
from users.models import Budget, Ledger


class Command(BaseCommand):
    """Export command."""

    help = "Export everything to json."

    def add_arguments(self, parser):
        """Add arguments for parser."""
        parser.add_argument("-u", "--username", required=True)
        parser.add_argument("-r", "--renumber-entries", action="store_true")
        parser.add_argument(
            "output", nargs="?", type=FileType("w", encoding="utf8"), default=sys.stdout
        )

    def handle(self, *args, **options):
        """Handle command."""
        data = {"accounts": []}
        for account in Ledger.objects.get(
            user__username=options["username"]
        ).accounts.all():
            if options["renumber_entries"]:
                account.renumber_entries()
            data["accounts"].append(
                {
                    "name": account.name,
                    "short_name": account.short_name,
                    "category": account.category.name,
                    "closed": account.closed,
                    "unit": {
                        "name": account.unit.name,
                        "code": account.unit.code,
                        "symbol": account.unit.symbol,
                        "precision": account.unit.precision,
                    },
                    "statements": [
                        {"name": statement.name, "file": statement.file.path}
                        for statement in account.statements.all()
                    ],
                    "entries": [
                        {
                            "serial_number": entry.serial_number,
                            "date": entry.day.strftime("%Y-%m-%d"),
                            "amount": entry.amount,
                            "fees": entry.fees,
                            "category": entry.category.name,
                            "text": entry.additional if entry.additional else None,
                            "tags": [tag.name for tag in entry.tags.all()],
                            "invoices": [
                                {"name": invoice.name, "file": invoice.file.path}
                                for invoice in entry.invoices.all()
                            ],
                        }
                        for entry in account.entries.all()
                    ],
                }
            )

        budget = Budget.objects.get(user__username=options["username"])
        data["budget"] = {
            "income_tags": [tag.name for tag in budget.income_tags.all()],
            "consumption_tags": [tag.name for tag in budget.consumption_tags.all()],
            "insurance_tags": [tag.name for tag in budget.insurance_tags.all()],
            "savings_tags": [tag.name for tag in budget.savings_tags.all()],
        }

        options["output"].write(json.dumps(data, indent=4, ensure_ascii=False))
        options["output"].write("\n")
