# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Ledger Django app models."""

import os

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, Func
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from units.models import Unit

from .fields import SingleLineTextField


def get_file_path(instance, filename):
    """Get file path."""
    name = slugify(instance.name) + os.path.splitext(filename)[1]
    if (
        isinstance(instance.content_object, Account)
        or type(instance.content_object).__name__ == Account.__name__
    ):
        return os.path.join(instance.content_object.slug, "files", name)
    elif (
        isinstance(instance.content_object, Entry)
        or type(instance.content_object).__name__ == Entry.__name__
    ):
        return os.path.join(
            instance.content_object.account.slug,
            "entries",
            str(instance.content_object.pk),
            name,
        )


class Category(models.Model):
    """Category model."""

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    name = SingleLineTextField(_("Name"), unique=True)

    def __str__(self):
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = (Func(F("name"), function="LOWER"),)
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Tag(models.Model):
    """Tag model."""

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    name = SingleLineTextField(_("Name"), unique=True)

    def __str__(self):
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = (Func(F("name"), function="LOWER"),)
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Account(models.Model):
    """Account model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    name = SingleLineTextField(unique=True, verbose_name=_("Name"))
    unit = models.ForeignKey(
        Unit, models.CASCADE, related_name="accounts", verbose_name=_("Unit")
    )
    category = models.ForeignKey(
        Category, models.CASCADE, related_name="accounts", verbose_name=_("Category")
    )
    closed = models.BooleanField(default=False, verbose_name=_("Closed"))
    files = GenericRelation(
        "File", related_query_name="accounts", verbose_name=_("Files")
    )

    def delete(self, *args, **kwargs):
        """Delete."""
        for file in self.files.all():
            file.delete()
        super().delete(*args, **kwargs)

    def renumber_entries(self):
        """Renumber entries."""
        for i, entry in enumerate(self.entries.all()):
            entry.serial_number = i + 1
            entry.save()

    def save(self, *args, **kwargs):
        """Save."""
        if not hasattr(self, "category") or self.category is None:
            self.category = Category.objects.get_or_create(name=self.name)[0]
        if self.slug is None or self.pk is None:
            self.slug = slugify(self.name)
        else:
            orig = Account.objects.get(pk=self.pk)
            if orig.name != self.name:
                self.slug = slugify(self.name)
                self.category.name = self.name
                self.category.save()
        super().save(*args, **kwargs)

    def __str__(self):
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = ("closed", Func(F("name"), function="LOWER"))
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")


class Entry(models.Model):
    """Entry model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    account = models.ForeignKey(
        Account, models.CASCADE, related_name="entries", verbose_name=_("Account")
    )
    serial_number = models.IntegerField(verbose_name=_("Serial number"))
    date = models.DateField(verbose_name=_("Date"))
    amount = models.FloatField(default=0.0, verbose_name=_("Amount"))
    fees = models.FloatField(default=0.0, verbose_name=_("Fees"))
    category = models.ForeignKey(
        Category, models.CASCADE, related_name="entries", verbose_name=_("Category")
    )
    text = SingleLineTextField(blank=True, null=True, verbose_name=_("Text"))
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="entries", verbose_name=_("Tags")
    )
    files = GenericRelation("File", related_query_name="files", verbose_name=_("Files"))

    def delete(self, *args, **kwargs):
        """Delete."""
        for file in self.files.all():
            file.delete()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Save."""
        move = False
        old_account = None
        if self.id:
            orig = Entry.objects.get(id=self.id)
            entry = (
                Entry.objects.filter(account=self.account)
                .filter(date__lte=self.date)
                .last()
            )
            next_snr = entry.serial_number + 1 if entry else 1
            if orig.date != self.date and (orig.serial_number + 1) != next_snr:
                move = True
            if orig.account != self.account:
                move = True
                self.serial_number = None
                old_account = orig.account
        if not self.id or move:
            entries = Entry.objects.filter(account=self.account).filter(
                date__lte=self.date
            )
            if entries.exists():
                next_snr = entries.last().serial_number + 1
            else:
                next_snr = 1

            entries = Entry.objects.filter(account=self.account).filter(
                serial_number__gte=next_snr
            )
            for entry in entries.reverse():
                entry.serial_number += 1
                entry.save()
            self.serial_number = next_snr
        super().save()

        if old_account:
            old_account.renumber_entries()

    def __str__(self):
        """Name."""
        return f"{self.account.name} #{self.serial_number}"

    class Meta:
        """Meta."""

        ordering = (Func(F("account__name"), function="LOWER"), "serial_number")
        unique_together = ("account", "serial_number")
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")


class File(models.Model):
    """File."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=1024, unique=True, verbose_name=_("Slug"))
    name = SingleLineTextField(verbose_name=_("Name"))
    file = models.FileField(
        upload_to=get_file_path, max_length=4096, verbose_name=_("File")
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def get_absolute_url(self):
        """Get absolute URL."""
        return reverse_lazy("file_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        """Save."""

        def make_slug():
            if (
                isinstance(self.content_object, Account)
                or type(self.content_object).__name__ == Account.__name__
            ):
                return slugify(f"{self.content_object.name} {self.name}")
            elif (
                isinstance(self.content_object, Entry)
                or type(self.content_object).__name__ == Entry.__name__
            ):
                return slugify(
                    f"{self.content_object.account.name} {self.content_object.pk} "
                    + f"{self.name}"
                )

        if not self.pk:
            self.slug = make_slug()
        else:
            orig = File.objects.get(pk=self.pk)
            if (
                orig.name != self.name
                or orig.content_type != self.content_type
                or orig.object_id != self.object_id
            ):
                self.slug = make_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        """Name."""
        return self.name

    class Meta:
        """Meta."""

        ordering = ("-updated_at", Func(F("name"), function="LOWER"))
        unique_together = ("content_type", "object_id", "name")
        verbose_name = _("File")
        verbose_name_plural = _("Files")


class Budget(models.Model):
    """Budget model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    income_tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="income_tags",
        verbose_name=_("Income tags"),
    )
    consumption_tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="consumption_tags",
        verbose_name=_("Consumption tags"),
    )
    insurance_tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="insurance_tags",
        verbose_name=_("Insurance tags"),
    )
    savings_tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="savings_tags",
        verbose_name=_("Savings tags"),
    )

    def get_absolute_url(self):
        """Get absolute URL."""
        return reverse_lazy("ledger:budget_detail")

    def __str__(self):
        """Name."""
        return "Budget"

    class Meta:
        """Meta."""

        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")
