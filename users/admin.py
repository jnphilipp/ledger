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

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from users.models import Budget, Ledger


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "user",
                    "income_tags",
                    "consumption_tags",
                    "insurance_tags",
                    "savings_tags",
                ]
            },
        ),
    ]
    filter_horizontal = (
        "income_tags",
        "consumption_tags",
        "insurance_tags",
        "savings_tags",
    )
    list_display = ("user", "updated_at")
    list_filter = ("user",)
    search_fields = (
        "user",
        "income_tags__name",
        "consumption_tags__name",
        "insurance_tags__name",
        "savings_tags__name",
    )


@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Ledger.objects.annotate(account_count=Count("accounts"))

    def show_account_count(self, inst):
        return inst.account_count

    fieldsets = [
        (None, {"fields": ["user", "accounts"]}),
    ]
    filter_horizontal = ("accounts",)
    list_display = ("user", "show_account_count", "updated_at")
    list_filter = ("user", "accounts")
    search_fields = ("user", "account__name")
    show_account_count.admin_order_field = "account_count"
    show_account_count.short_description = _("Number of Accounts")
