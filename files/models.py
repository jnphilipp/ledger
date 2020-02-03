# -*- coding: utf-8 -*-

import os

from accounts.models import Account, Entry
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from ledger.fields import SingleLineTextField


def get_file_path(instance, filename):
    name = slugify(instance.name) + os.path.splitext(filename)[1]
    if isinstance(instance, Statement):
        return os.path.join('files', 'account', str(instance.account.pk),
                            'statements', name)
    elif isinstance(instance, Invoice):
        return os.path.join('files', 'account', str(instance.entry.account.pk),
                            'entries', str(instance.entry.pk), name)


class File(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Updated at'))

    slug = models.SlugField(max_length=1024, unique=True,
                            verbose_name=_('Slug'))
    name = SingleLineTextField(verbose_name=_('Name'))
    file = models.FileField(upload_to=get_file_path, max_length=4096,
                            verbose_name=_('File'))
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE,
                                 verbose_name=_('User'))

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)
        verbose_name = _('File')
        verbose_name_plural = _('Files')


class Invoice(File):
    entry = models.ForeignKey(Entry, models.CASCADE,
                              related_name='invoices',
                              verbose_name=_('Entry'))

    def get_absolute_url(self):
        return reverse_lazy('files:invoice_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(f'{self.entry.account.pk} {self.entry.pk}' +
                                f' {self.name}')
        else:
            orig = Invoice.objects.get(pk=self.pk)
            if orig.name != self.name or orig.entry != self.entry:
                self.slug = slugify(f'{self.entry.account.pk} ' +
                                    f'{self.entry.pk} {self.name}')
        super(Invoice, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('entry', 'name')
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')


class Statement(File):
    account = models.ForeignKey(Account, models.CASCADE,
                                related_name='statements',
                                verbose_name=_('Account'))

    def get_absolute_url(self):
        return reverse_lazy('files:statement_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(f'{self.account.pk} {self.name}')
        else:
            orig = Statement.objects.get(pk=self.pk)
            if orig.name != self.name or orig.account != self.account:
                self.slug = slugify(f'{self.account.pk} {self.name}')
        super(Statement, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('account', 'name')
        verbose_name = _('Statement')
        verbose_name_plural = _('Statements')


class OldFile(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    slug = models.SlugField(
        max_length=1024,
        unique=True,
        verbose_name=_('Slug')
    )
    name = SingleLineTextField(
        verbose_name=_('Name')
    )
    file = models.FileField(
        upload_to=get_file_path,
        max_length=4096,
        verbose_name=_('File')
    )

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_('User')
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('File')
        verbose_name_plural = _('Files')
