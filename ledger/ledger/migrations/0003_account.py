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
# Generated by Django 4.0 on 2022-01-14 09:01

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import ledger.fields


class Migration(migrations.Migration):

    dependencies = [
        ("units", "0002_default_units"),
        ("ledger", "0002_tag"),
    ]

    operations = [
        migrations.CreateModel(
            name="Account",
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
                ("slug", models.SlugField(unique=True, verbose_name="Slug")),
                (
                    "name",
                    ledger.fields.SingleLineTextField(unique=True, verbose_name="Name"),
                ),
                ("closed", models.BooleanField(default=False, verbose_name="Closed")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accounts",
                        to="ledger.category",
                        verbose_name="Category",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accounts",
                        to="units.unit",
                        verbose_name="Unit",
                    ),
                ),
            ],
            options={
                "verbose_name": "Account",
                "verbose_name_plural": "Accounts",
                "ordering": (
                    "closed",
                    django.db.models.expressions.Func(
                        django.db.models.expressions.F("name"), function="LOWER"
                    ),
                ),
            },
        ),
    ]
