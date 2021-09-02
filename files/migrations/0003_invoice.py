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
# Generated by Django 2.2.8 on 2020-01-04 12:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import files.models
import ledger.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0004_entry_fees'),
        ('files', '0002_rename_file_oldfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('slug', models.SlugField(max_length=1024, unique=True, verbose_name='Slug')),
                ('name', ledger.fields.SingleLineTextField(verbose_name='Name')),
                ('file', models.FileField(max_length=4096, upload_to=files.models.get_file_path, verbose_name='File')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='accounts.Entry', verbose_name='Entry')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
            },
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('entry', 'name')]),
        ),
    ]
