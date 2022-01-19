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
"""Units Django app admin."""

from django.contrib import admin

from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Unit Django admin."""

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "name",
                    "code",
                    "symbol",
                    "precision",
                ]
            },
        ),
    ]
    list_display = ("name", "code", "symbol", "precision")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name", "code", "symbol")
