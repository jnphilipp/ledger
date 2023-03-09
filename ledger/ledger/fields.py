# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2023 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Ledger Django app fields."""

from django.db import connection
from django.db.models.fields import Field
from django.utils.translation import gettext_lazy as _


class SingleLineTextField(Field):
    """SingleLineTextField model field."""

    description = _("Text")

    def get_internal_type(self):
        """Get Internal type."""
        return "TextField"

    def to_python(self, value):
        """To Python."""
        if isinstance(value, str) or value is None:
            return value
        return str(value)

    def get_prep_value(self, value):
        """Prep value."""
        value = super().get_prep_value(value)
        return self.to_python(value)

    def formfield(self, **kwargs):
        """Formfield."""
        defaults = {"max_length": self.max_length}
        if self.null and not connection.features.interprets_empty_strings_as_nulls:
            defaults["empty_value"] = None
        defaults.update(kwargs)
        field = super().formfield(**defaults)
        return field
