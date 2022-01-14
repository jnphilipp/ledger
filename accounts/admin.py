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

from accounts.models import Account, Entry
from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Account.objects.annotate(entry_count=Count("entries"))

    def show_entry_count(self, inst):
        return inst.entry_count

    def get_ledgers(self, obj):
        return ", ".join([str(ledger) for ledger in obj.ledgers.all()])

    fieldsets = [
        (None, {"fields": ["ledgers", "slug", "name", "short_name", "category", "unit"]}),
    ]
    filter_horizontal = ("ledgers",)
    get_ledgers.short_description = _("Ledgers")
    list_display = ("name", "get_ledgers", "show_entry_count", "unit", "updated_at")
    list_filter = ("unit", "ledger")
    readonly_fields = ("slug",)
    search_fields = ("name", "unit__name")
    show_entry_count.admin_order_field = "entry_count"
    show_entry_count.short_description = _("Number of entries")


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "serial_number",
                    "day",
                    "amount",
                    "category",
                    "additional",
                    "tags",
                ]
            },
        ),
    ]
    filter_horizontal = ("tags",)
    list_display = (
        "account",
        "serial_number",
        "day",
        "category",
        "additional",
        "updated_at",
    )
    list_filter = ("account", "category", "day", "tags")
