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
# Generated by Django 4.0 on 2022-01-18 14:44

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import ledger.fields
import ledger.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ledger', '0004_entry'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('slug', models.SlugField(max_length=1024, unique=True, verbose_name='Slug')),
                ('name', ledger.fields.SingleLineTextField(verbose_name='Name')),
                ('file', models.FileField(max_length=4096, upload_to=ledger.models.get_file_path, verbose_name='File')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
                'ordering': ('-updated_at', django.db.models.expressions.Func(django.db.models.expressions.F('name'), function='LOWER')),
                'unique_together': {('content_type', 'object_id', 'name')},
            },
        ),
    ]
