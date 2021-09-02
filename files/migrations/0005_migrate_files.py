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
# Generated by Django 2.2.8 on 2020-01-04 12:40

import os

from django.contrib.contenttypes.models import ContentType
from django.core.files import File as DJFile
from django.db import migrations
from django.template.defaultfilters import slugify


def migrate_files(apps, schema_editor):
    File = apps.get_model('files', 'OldFile')
    Invoice = apps.get_model('files', 'Invoice')
    Statement = apps.get_model('files', 'Statement')

    Account = apps.get_model('accounts', 'Account')
    account_type = ContentType.objects.get_for_model(Account)
    Entry = apps.get_model('accounts', 'Entry')
    entry_type = ContentType.objects.get_for_model(Entry)
    for file in File.objects.all():
        name = f'{slugify(file.name)}{os.path.splitext(file.file.name)[1]}'
        if file.content_type_id == account_type.pk:
            statement = Statement()
            statement.name = file.name
            statement.uploader = file.uploader
            statement.account = Account.objects.get(pk=file.object_id)
            statement.slug = \
                slugify(f'{statement.account.slug} {statement.name}')
            statement.created_at = file.created_at
            statement.updated_at = file.updated_at
            statement.file.save(name, DJFile(open(file.file.path, 'rb')))
            statement.save()
        elif file.content_type_id == entry_type.pk:
            invoice = Invoice()
            invoice.name = file.name
            invoice.entry = Entry.objects.get(pk=file.object_id)
            invoice.slug = slugify(f'{invoice.entry.account.pk} ' +
                                   f'{invoice.entry.pk} {invoice.name}')
            invoice.uploader = file.uploader
            invoice.created_at = file.created_at
            invoice.updated_at = file.updated_at
            invoice.file.save(name, DJFile(open(file.file.path, 'rb')))
            invoice.save()
        file.delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('files', '0004_statement'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('accounts', '0004_entry_fees'),
    ]

    operations = [
        migrations.RunPython(migrate_files),
    ]
