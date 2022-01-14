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
"""Ledger Django app import command."""

import json
import os
import sys

from accounts.models import Account, Entry
from argparse import FileType
from categories.models import Category, Tag
from django.core.files import File
from django.core.management.base import BaseCommand
from files.models import Invoice, Statement
from ledger.models import Budget
from units.models import Unit


class Command(BaseCommand):
    """Import command."""

    help = "Import everything from json."

    def add_arguments(self, parser):
        """Add arguments for parser."""
        parser.add_argument("-r", "--renumber-entries", action="store_true")
        parser.add_argument(
            "JSON", nargs="?", type=FileType("r", encoding="utf8"), default="-"
        )

    def handle(self, *args, **options):
        """Handle command."""
        data = json.loads(options["JSON"].read())

        if "accounts" in data:
            for a in data["accounts"]:
                if "code" in a["unit"]:
                    unit = Unit.objects.get(code=a["unit"]["code"])
                else:
                    try:
                        unit = Unit.objects.get(
                            name=a["unit"]["name"],
                            precision=a["unit"]["precision"],
                        )
                    except Unit.DoesNotExist:
                        self.stderr.write(
                            self.style.ERROR(
                                f"Unit {a['unit']['name']} not found."
                            )
                        )
                        sys.exit(0)

                category, created = Category.objects.get_or_create(
                    name=a["category"]
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Category {category} successfully "
                        + f"{'created' if created else 'updated'}."
                    )
                )

                if Account.objects.filter(name=a["name"]).exists():
                    self.stderr.write(
                        self.style.ERROR(
                            f"Account {a['name']} already exists, skipping..."
                        )
                    )
                    continue

                account = Account.objects.create(
                    name=a["name"],
                    short_name=a["short_name"] if "short_name" in a else None,
                    category=category,
                    unit=unit,
                    closed=a["closed"],
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Account {account} successfully created."
                    )
                )

                for e in a["entries"]:
                    category, created = Category.objects.get_or_create(
                        name=e["category"]
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Category {category} successfully "
                            + f"{'created' if created else 'updated'}."
                        )
                    )

                    entry = Entry.objects.create(
                        serial_number=e["serial_number"],
                        date=e["date"],
                        amount=e["amount"],
                        fees=e["fees"],
                        category=category,
                        additional=e["text"],
                        account=account,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Entry {entry} successfully created."
                        )
                    )

                    for t in e["tags"]:
                        tag, created = Tag.objects.get_or_create(name=t)
                        entry.tags.add(tag)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Tag {tag} successfully "
                                + f"{'created' if created else 'updated'}."
                            )
                        )
                    if "invoices" in a:
                        for i in a["invoices"]:
                            invoice = Invoice(name=i["name"], entry=entry)
                            invoice.file.save(
                                os.path.basename(i["file"]), File(open(i["file"], "rb"))
                            )
                            invoice.save()
                for s in a["statements"]:
                    statement = Statement(name=s["name"], account=account)
                    statement.file.save(
                        os.path.basename(s["file"]), File(open(s["file"], "rb"))
                    )
                    statement.save()
        else:
            self.stdout.write(
                self.style.ERROR("No accounts found in data, aborting...")
            )
            sys.exit(1)

        if "budget" in data:
            budget, created = Budget.objects.get_or_create()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Budget successfully {'created' if created else 'updated'}."
                )
            )

            for t in data["budget"]["income_tags"]:
                budget.income_tags.add(Tag.objects.get(name=t))
            for t in data["budget"]["consumption_tags"]:
                budget.consumption_tags.add(Tag.objects.get(name=t))
            for t in data["budget"]["insurance_tags"]:
                budget.insurance_tags.add(Tag.objects.get(name=t))
            for t in data["budget"]["savings_tags"]:
                budget.savings_tags.add(Tag.objects.get(name=t))
        else:
            self.stdout.write(self.style.ERROR("No budget found in data."))
        # data = {"accounts": []}
        # for account in Ledger.objects.get(
        #     user__username=options["username"]
        # ).accounts.all():
        #     if options["renumber_entries"]:
        #         account.renumber_entries()
        #     data["accounts"].append(
        #         {
        #             "name": account.name,
        #             "category": account.category.name,
        #             "closed": account.closed,
        #             "unit": {
        #                 "name": account.unit.name,
        #                 "symbol": account.unit.symbol,
        #                 "precision": account.unit.precision,
        #             },
        #             "statements": [
        #                 {"name": statement.name, "file": statement.file.path}
        #                 for statement in account.statements.all()
        #             ],
        #             "entries": [
        #                 {
        #                     "serial_number": entry.serial_number,
        #                     "date": entry.day.strftime("%Y-%m-%d"),
        #                     "amount": entry.amount,
        #                     "fees": entry.fees,
        #                     "category": entry.category.name,
        #                     "text": entry.additional if entry.additional else None,
        #                     "tags": [tag.name for tag in entry.tags.all()],
        #                     "invoices": [
        #                         {"name": invoice.name, "file": invoice.file.path}
        #                         for invoice in entry.invoices.all()
        #                     ],
        #                 }
        #                 for entry in account.entries.all()
        #             ],
        #         }
        #     )

        # budget = Budget.objects.get(user__username=options["username"])
        # data["budget"] = {
        #     "income_tags": [tag.name for tag in budget.income_tags.all()],
        #     "consumption_tags": [tag.name for tag in budget.consumption_tags.all()],
        #     "insurance_tags": [tag.name for tag in budget.insurance_tags.all()],
        #     "savings_tags": [tag.name for tag in budget.savings_tags.all()],
        # }

        # options["output"].write(json.dumps(data, indent=4, ensure_ascii=False))
        # options["output"].write("\n")
