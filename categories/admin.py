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

from categories.models import Category, Tag
from django.contrib import admin


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["slug", "name"]}),
    ]
    list_display = ("name", "updated_at")
    readonly_fields = ("slug",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["slug", "name"]}),
    ]
    list_display = ("name", "updated_at")
    readonly_fields = ("slug",)
    search_fields = ("name",)
