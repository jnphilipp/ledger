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
# Generated by Django 3.2.6 on 2021-10-07 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('portfolio', '0003_etf'),
    ]

    operations = [
        migrations.CreateModel(
            name='Closing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('date', models.DateField(verbose_name='Date')),
                ('price', models.FloatField(verbose_name='Price')),
                ('high', models.FloatField(default=0, verbose_name='High')),
                ('low', models.FloatField(default=0, verbose_name='Low')),
                ('change_previous', models.FloatField(default=0, verbose_name='Absolute change')),
                ('change_previous_percent', models.FloatField(default=0, verbose_name='Relative change')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closings', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Closing',
                'verbose_name_plural': 'Closings',
                'ordering': ('content_type', 'object_id', '-date'),
                'unique_together': {('date', 'content_type', 'object_id')},
            },
        ),
    ]
