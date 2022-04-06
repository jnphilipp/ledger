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
# Generated by Django 3.2.6 on 2021-10-07 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),
        ('portfolio', '0005_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('serial_number', models.IntegerField(verbose_name='Serial number')),
                ('date', models.DateField(verbose_name='Date')),
                ('units', models.FloatField(default=0., verbose_name='Units')),
                ('unit_price', models.FloatField(default=0., verbose_name='Unit price')),
                ('extra', models.FloatField(default=0., verbose_name='Extra costs')),
                ('extra2', models.FloatField(default=0., verbose_name='Extra costs')),
                ('exchange_rate', models.FloatField(blank=True, null=True, verbose_name='Exchange rate')),
                ('type', models.IntegerField(choices=[(None, '(Unknown)'), (0, 'Buy'), (1, 'Sell'), (2, 'Dividend'), (3, 'Pre-emption right')], verbose_name='Type')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', to='portfolio.position', verbose_name='Position')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', to='units.unit', verbose_name='Unit')),
            ],
            options={
                'verbose_name': 'Trade',
                'verbose_name_plural': 'Trades',
                'ordering': ('position', '-serial_number'),
                'unique_together': {('position', 'serial_number')},
            },
        ),
    ]
