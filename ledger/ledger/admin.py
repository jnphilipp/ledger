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
"""Ledger Django app admin."""

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .models import Account, Budget, Category, Entry, File, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin."""

    fieldsets = [
        (None, {"fields": ["created_at", "updated_at", "name"]}),
    ]
    list_display = ("name", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag admin."""

    fieldsets = [
        (None, {"fields": ["created_at", "updated_at", "name"]}),
    ]
    list_display = ("name", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Account admin."""

    def get_queryset(self, request):
        """Get queryset."""
        return Account.objects.annotate(entry_count=Count("entries"))

    def show_entry_count(self, inst):
        """Show entry count."""
        return inst.entry_count

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "slug",
                    "name",
                    "short_name",
                    "category",
                    "unit",
                ]
            },
        ),
    ]
    filter_horizontal = ("ledgers",)
    list_display = ("name", "show_entry_count", "unit", "updated_at")
    list_filter = ("unit",)
    readonly_fields = ("created_at", "updated_at", "slug")
    search_fields = ("name", "unit__name")
    show_entry_count.admin_order_field = "entry_count"
    show_entry_count.short_description = _("Number of entries")


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """Entry admin."""

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "serial_number",
                    "day",
                    "amount",
                    "category",
                    "text",
                ]
            },
        ),
        (_("Tags"), {"fields": ["tags"]}),
    ]
    filter_horizontal = ("tags",)
    list_display = (
        "account",
        "serial_number",
        "day",
        "category",
    )
    list_filter = ("account", "category", "day", "tags")
    readonly_fields = ("created_at", "updated_at")


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """File admin."""

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "slug",
                    "name",
                    "file",
                    "content_type",
                    "object_id",
                ]
            },
        ),
    ]
    list_display = ("name", "entry", "content_type", "object_id", "updated_at")
    list_filter = ("content_type", "object_id")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at", "slug")


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Budget admin."""

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created_at",
                    "updated_at",
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
    list_display = ("pk", "updated_at")
    ordering = ("pk",)
    readonly_fields = ("created_at", "updated_at", "slug")
