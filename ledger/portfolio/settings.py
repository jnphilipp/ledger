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
"""Portfolio Django app settings."""

from django.conf import settings


SETTINGS = getattr(settings, "CLOSING_FORM_DEFAULTS", {})

CLOSING_FORM_DATEFORMAT = "%Y-%m-%d"
if "DATEFORMAT" in SETTINGS:
    CLOSING_FORM_DATEFORMAT = SETTINGS["DATEFORMAT"]


CLOSING_FORM_INITIAL_DATE_FIELD = None
if "INITIAL_DATE_FIELD" in SETTINGS:
    CLOSING_FORM_INITIAL_DATE_FIELD = SETTINGS["INITIAL_DATE_FIELD"]


CLOSING_FORM_INITIAL_PRICE_FIELD = None
if "INITIAL_PRICE_FIELD" in SETTINGS:
    CLOSING_FORM_INITIAL_PRICE_FIELD = SETTINGS["INITIAL_PRICE_FIELD"]


CLOSING_FORM_INITIAL_LOW_FIELD = None
if "INITIAL_LOW_FIELD" in SETTINGS:
    CLOSING_FORM_INITIAL_LOW_FIELD = SETTINGS["INITIAL_LOW_FIELD"]


CLOSING_FORM_INITIAL_HIGH_FIELD = None
if "INITIAL_HIGH_FIELD" in SETTINGS:
    CLOSING_FORM_INITIAL_HIGH_FIELD = SETTINGS["INITIAL_HIGH_FIELD"]
