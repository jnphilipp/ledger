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

from django.contrib.contenttypes.models import ContentType
from django.template import Library


register = Library()


@register.filter
def get_item(d, key):
    if type(d) == dict:
        return d[key] if key in d else None
    else:
        return d[key] if key < len(d) else None


@register.filter
def startswith(value, start):
    return value.startswith(start)


@register.filter
def endswith(value, start):
    return value.endswith(start)


@register.filter
def previous(value, arg):
    try:
        return value[int(arg) - 1] if int(arg) - 1 != -1 else None
    except IndexError:
        return None


@register.filter
def next(value, arg):
    try:
        return value[int(arg) + 1]
    except IndexError:
        return None


@register.filter
def mod(num, val):
    return num % val


@register.filter
def content_type_pk(model):
    return ContentType.objects.get_for_model(model).pk
