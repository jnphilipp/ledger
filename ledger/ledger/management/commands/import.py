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
"""Ledger Django app import command."""

import json
import os
import sys

from argparse import FileType
from django.core.files import File as DJFile
from django.core.management.base import BaseCommand
from units.models import Unit

from ...models import Account, Budget, Category, Entry, File, Tag


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
                            self.style.ERROR(f"Unit {a['unit']['name']} not found.")
                        )
                        sys.exit(0)

                category, created = Category.objects.get_or_create(name=a["category"])
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Category {category} successfully created.")
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
                    category=category,
                    unit=unit,
                    closed=a["closed"],
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Account {account} successfully created.")
                )

                for e in a["entries"]:
                    category, created = Category.objects.get_or_create(
                        name=e["category"]
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Category {category} successfully created."
                            )
                        )

                    entry = Entry.objects.create(
                        serial_number=e["serial_number"],
                        date=e["date"],
                        amount=e["amount"],
                        fees=e["fees"],
                        category=category,
                        text=e["text"],
                        account=account,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Entry {entry} successfully created.")
                    )

                    for t in e["tags"]:
                        tag, created = Tag.objects.get_or_create(name=t)
                        entry.tags.add(tag)
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(f"Tag {tag} successfully created.")
                            )
                    if "files" in e:
                        for i in e["files"]:
                            file = File(name=i["name"], content_object=entry)
                            file.file.save(
                                os.path.basename(i["file"]),
                                DJFile(open(i["file"], "rb")),
                            )
                            file.save()
                            self.stdout.write(
                                self.style.SUCCESS(f"File {file} successfully created.")
                            )
                if "files" in a:
                    for s in a["files"]:
                        file = File(name=s["name"], content_object=account)
                        file.file.save(
                            os.path.basename(s["file"]), DJFile(open(s["file"], "rb"))
                        )
                        file.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"File {file} successfully created.")
                        )
        else:
            self.stdout.write(
                self.style.ERROR("No accounts found in data, aborting...")
            )
            sys.exit(1)

        if "budget" in data:
            budget, created = Budget.objects.get_or_create()
            if created:
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
