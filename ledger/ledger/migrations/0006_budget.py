# Copyright (C) 2014-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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


class Migration(migrations.Migration):

    dependencies = [
        ("ledger", "0005_file"),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "consumption_tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="consumption_tags",
                        to="ledger.Tag",
                        verbose_name="Consumption tags",
                    ),
                ),
                (
                    "income_tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="income_tags",
                        to="ledger.Tag",
                        verbose_name="Income tags",
                    ),
                ),
                (
                    "insurance_tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="insurance_tags",
                        to="ledger.Tag",
                        verbose_name="Insurance tags",
                    ),
                ),
                (
                    "savings_tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="savings_tags",
                        to="ledger.Tag",
                        verbose_name="Savings tags",
                    ),
                ),
            ],
            options={
                "verbose_name": "Budget",
                "verbose_name_plural": "Budgets",
            },
        ),
    ]
