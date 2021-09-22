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
# Generated by Django 3.2.6 on 2021-09-22 23:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('portfolio', '0002_closing'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('day', models.DateField(verbose_name='Day')),
                ('units', models.FloatField(verbose_name='Units')),
                ('unit_price', models.FloatField(verbose_name='Unit price')),
                ('extra', models.FloatField(verbose_name='Extra')),
                ('type', models.IntegerField(choices=[(None, '(Unknown)'), (0, 'Buy'), (1, 'Sell'), (2, 'Dividend')], verbose_name='Type')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolios_trade_content_type', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Trade',
                'verbose_name_plural': 'Trades',
                'ordering': ('day', 'type'),
            },
        ),
    ]
