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

import os

from accounts.models import Account, Entry
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from ledger.fields import SingleLineTextField


def get_file_path(instance, filename):
    name = slugify(instance.name) + os.path.splitext(filename)[1]
    if isinstance(instance, Statement) or type(instance).__name__ == Statement.__name__:
        return os.path.join("accounts", instance.account.slug, "statements", name)
    elif isinstance(instance, Invoice) or type(instance).__name__ == Invoice.__name__:
        return os.path.join(
            "accounts",
            instance.entry.account.slug,
            "entries",
            str(instance.entry.pk),
            name,
        )


class File(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=1024, unique=True, verbose_name=_("Slug"))
    name = SingleLineTextField(verbose_name=_("Name"))
    file = models.FileField(
        upload_to=get_file_path, max_length=4096, verbose_name=_("File")
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ("name",)
        verbose_name = _("File")
        verbose_name_plural = _("Files")


class Invoice(File):
    entry = models.ForeignKey(
        Entry, models.CASCADE, related_name="invoices", verbose_name=_("Entry")
    )

    def get_absolute_url(self):
        return reverse_lazy("files:invoice_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(
                f"{self.entry.account.slug} {self.entry.pk}" + f" {self.name}"
            )
        else:
            orig = Invoice.objects.get(pk=self.pk)
            if orig.name != self.name or orig.entry != self.entry:
                self.slug = slugify(
                    f"{self.entry.account.slug} " + f"{self.entry.pk} {self.name}"
                )
        super(Invoice, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("entry", "name")
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


class Statement(File):
    account = models.ForeignKey(
        Account, models.CASCADE, related_name="statements", verbose_name=_("Account")
    )

    def get_absolute_url(self):
        return reverse_lazy("files:statement_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(f"{self.account.slug} {self.name}")
        else:
            orig = Statement.objects.get(pk=self.pk)
            if orig.name != self.name or orig.account != self.account:
                self.slug = slugify(f"{self.account.slug} {self.name}")
        super(Statement, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("account", "name")
        verbose_name = _("Statement")
        verbose_name_plural = _("Statements")
