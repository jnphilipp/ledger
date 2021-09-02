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

from accounts.models import Account
from django.core.management.base import BaseCommand
from django.db.models import Q
from json import dumps


class Command(BaseCommand):
    help = "Exports an account with all its entries."

    def add_arguments(self, parser):
        parser.add_argument("-o", "--output", help="Output file")
        parser.add_argument("accounts", nargs="*", help="Accounts")

    def handle(self, *args, **options):
        accounts = Account.objects.all()
        if options["accounts"]:
            accounts = accounts.filter(
                Q(slug__in=options["accounts"]) | Q(name__in=options["accounts"])
            )
        data = []
        for account in accounts:
            account.renumber_entries()
            data.append(
                {
                    "name": account.name,
                    "closed": account.closed,
                    "category": account.category.name,
                    "unit": account.unit.name,
                    "entries": [
                        {
                            "nr": entry.serial_number,
                            "date": entry.day.strftime("%Y-%m-%d"),
                            "amount": entry.amount,
                            "fees": entry.fees,
                            "category": entry.category.name,
                            "text": entry.additional,
                            "tags": [tag.name for tag in entry.tags.all()],
                        }
                        for entry in account.entries.all()
                    ],
                }
            )
        if options["output"]:
            with open(options["output"], "w", encoding="utf8") as f:
                f.write(dumps(data, indent=4))
                f.write("\n")
        else:
            self.stdout.write(dumps(data, indent=4))
