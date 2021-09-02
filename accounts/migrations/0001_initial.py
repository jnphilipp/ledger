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
# Generated by Django 1.11.1 on 2017-06-27 07:20
from __future__ import unicode_literals

import accounts.models
import ledger.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('units', '0001_initial'),
        ('categories', '0002_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('name', ledger.fields.SingleLineTextField(verbose_name='Name')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='categories.Category', verbose_name='Category')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='units.Unit', verbose_name='Unit')),
            ],
            options={
                'verbose_name_plural': 'Accounts',
                'verbose_name': 'Account',
                'ordering': ('closed', 'name'),
            },
        ),
    ]
