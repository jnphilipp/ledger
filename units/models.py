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
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from ledger.fields import SingleLineTextField


class Unit(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=2048, unique=True, verbose_name=_("Slug"))
    name = SingleLineTextField(verbose_name=_("Name"))
    code = models.TextField(
        max_length=3,
        unique=True,
        verbose_name=_("Currency code (ISO 4217)")
    )
    symbol = SingleLineTextField(verbose_name=_("Symbol"))
    precision = models.PositiveIntegerField(default=2, verbose_name=_("Precision"))

    def get_absolute_url(self):
        return reverse_lazy("units:detail", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code)
        else:
            orig = Unit.objects.get(pk=self.id)
            if orig.code != self.code:
                self.slug = slugify(self.code)
        super(Unit, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")
