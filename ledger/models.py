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

from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class Budget(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    income_tags = models.ManyToManyField(
        "categories.Tag",
        blank=True,
        related_name="income_tags",
        verbose_name=_("Income tags"),
    )
    consumption_tags = models.ManyToManyField(
        "categories.Tag",
        blank=True,
        related_name="consumption_tags",
        verbose_name=_("Consumption tags"),
    )
    insurance_tags = models.ManyToManyField(
        "categories.Tag",
        blank=True,
        related_name="insurance_tags",
        verbose_name=_("Insurance tags"),
    )
    savings_tags = models.ManyToManyField(
        "categories.Tag",
        blank=True,
        related_name="savings_tags",
        verbose_name=_("Savings tags"),
    )

    def get_absolute_url(self):
        return reverse_lazy("ledger:budget_detail")

    def __str__(self):
        return "Budget"

    class Meta:
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")
