# -*- coding: utf-8 -*-

from categories.models import Category, Tag
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from ledger.fields import SingleLineTextField
from time import time
from units.models import Unit
from users.models import Ledger


class Account(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    name = SingleLineTextField(
        verbose_name=_('Name')
    )
    unit = models.ForeignKey(
        Unit,
        models.CASCADE,
        related_name='accounts',
        verbose_name=_('Unit')
    )
    category = models.ForeignKey(
        Category,
        models.CASCADE,
        related_name='accounts',
        verbose_name=_('Category')
    )
    ledgers = models.ManyToManyField(
        Ledger,
        through=Ledger.accounts.through,
        verbose_name=_('Ledgers')
    )
    closed = models.BooleanField(
        default=False,
        verbose_name=_('Closed')
    )
    statements = GenericRelation(
        'files.File',
        related_query_name='accounts',
        verbose_name=_('Statements')
    )

    def delete(self, *args, **kwargs):
        for file in self.statements:
            file.delete()
        super(Account, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('accounts:account', args=[self.slug])

    def renumber_entries(self):
        for i, entry in enumerate(self.entries.all()):
            entry.serial_number = i + 1
            entry.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            if not Account.objects.filter(slug=slugify(self.name)).exists():
                self.slug = slugify(self.name)
            else:
                self.slug = slugify('%s%s' % (int(round(time() * 1000)),
                                              self.name))
        else:
            orig = Account.objects.get(pk=self.id)
            if orig.name != self.name:
                if Account.objects.filter(slug=slugify(self.name)).exists():
                    self.slug = slugify('%s%s' % (int(round(time() * 1000)),
                                                  self.name))
                else:
                    self.slug = slugify(self.name)
        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('closed', 'name')
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')


class Entry(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    account = models.ForeignKey(
        Account,
        models.CASCADE,
        related_name='entries',
        verbose_name=_('Account')
    )
    serial_number = models.IntegerField(
        verbose_name=_('Serial number')
    )
    day = models.DateField(
        verbose_name=_('Day')
    )
    amount = models.FloatField(
        default=0,
        verbose_name=_('Amount')
    )
    category = models.ForeignKey(
        Category,
        models.CASCADE,
        related_name='entries',
        verbose_name=_('Category')
    )
    additional = SingleLineTextField(
        blank=True,
        null=True,
        verbose_name=_('Additional')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='entries',
        verbose_name=_('Tags')
    )
    files = GenericRelation(
        'files.File',
        related_query_name='entries',
        verbose_name=_('Files')
    )

    def delete(self, *args, **kwargs):
        for file in self.files.all():
            file.delete()
        super(Entry, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('accounts:account_entry',
                       args=[self.account.slug, self.pk])

    def save(self, *args, **kwargs):
        move = False
        old_account = None
        if self.id:
            orig = Entry.objects.get(id=self.id)
            entry = Entry.objects.filter(account=self.account). \
                filter(day__lte=self.day).last()
            next_snr = entry.serial_number + 1 if entry else 1
            if orig.day != self.day and (orig.serial_number + 1) != next_snr:
                move = True
            if orig.account != self.account:
                move = True
                self.serial_number = None
                old_account = orig.account
        if not self.id or move:
            entries = Entry.objects.filter(account=self.account). \
                filter(day__lte=self.day)
            if entries.exists():
                next_snr = entries.last().serial_number + 1
            else:
                next_snr = 1

            entries = Entry.objects.filter(account=self.account). \
                filter(serial_number__gte=next_snr)
            for entry in entries.reverse():
                entry.serial_number += 1
                entry.save()
            self.serial_number = next_snr
        super(Entry, self).save()

        if old_account:
            old_account.renumber_entries()

    class Meta:
        ordering = ('account', 'serial_number')
        unique_together = ('account', 'serial_number')
        verbose_name = _('Entry')
        verbose_name_plural = _('Entries')
