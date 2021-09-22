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
"""Portfolio Django app models."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from units.models import Unit


class Stock(models.Model):
    """Stock ORM Model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    name = models.CharField(max_length=1024, unique=True, verbose_name=_("Name"))
    isin = models.CharField(max_length=12, unique=True, verbose_name=_("ISIN"))
    wkn = models.CharField(
        max_length=6, unique=True, blank=True, null=True, verbose_name=_("WKN")
    )
    symbol = models.CharField(
        max_length=12, unique=True, blank=True, null=True, verbose_name=_("Symbol")
    )
    currency = models.ForeignKey(
        Unit,
        models.SET_NULL,
        related_name="stocks",
        blank=True,
        null=True,
        verbose_name=_("Currency"),
    )
    traded = models.BooleanField(default=True, verbose_name=_("Traded"))

    def get_absolute_url(self):
        """Get absolute URL."""
        return reverse_lazy("portfolio:stock_detail", args=[self.stock.slug])

    def save(self, *args, **kwargs):
        """Save."""
        if not self.slug:
            self.slug = slugify(f"{self.name} {self.isin}")
        else:
            orig = Stock.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(f"{self.name} {self.isin}")
        super(Stock, self).save(*args, **kwargs)

    def __str__(self) -> str:
        """Name."""
        return f"{self.name} [{self.symbol}]"

    class Meta:
        """Meta."""

        ordering = ("name",)
        verbose_name = _("Stock")
        verbose_name_plural = _("Stocks")


class Closing(models.Model):
    """Closing ORM Model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    day = models.DateField(verbose_name=_("Day"))
    price = models.FloatField(verbose_name=_("Price"))
    high = models.FloatField(default=0, verbose_name=_("High"))
    low = models.FloatField(default=0, verbose_name=_("Low"))
    change_previous = models.FloatField(default=0, verbose_name=_("Absolute change"))
    change_previous_percent = models.FloatField(
        default=0, verbose_name=_("Relative change")
    )
    content_type = models.ForeignKey(
        ContentType, models.CASCADE, related_name="closings"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self) -> str:
        """Name."""
        return f"{self.content_type} {self.object_id} [{self.day}]"

    class Meta:
        """Meta."""

        ordering = ("content_type", "object_id", "-day")
        unique_together = ("day", "content_type", "object_id")
        verbose_name = _("Closing")
        verbose_name_plural = _("Closings")
