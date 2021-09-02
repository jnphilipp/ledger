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

import os

from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from files.models import Invoice, Statement


@receiver(pre_delete, sender=Invoice)
def delete_invoice_file(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
    except FileNotFoundError:
        pass


@receiver(pre_delete, sender=Statement)
def delete_statement_file(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
    except FileNotFoundError:
        pass
