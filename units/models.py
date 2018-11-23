# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from ledger.fields import SingleLineTextField


class Unit(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    slug = models.SlugField(
        max_length=2048,
        unique=True,
        verbose_name=_('Slug')
    )
    name = SingleLineTextField(
        unique=True,
        verbose_name=_('Name')
    )
    symbol = SingleLineTextField(
        unique=True,
        verbose_name=_('Symbol')
    )
    precision = models.PositiveIntegerField(
        default=2,
        verbose_name=_('Precision')
    )

    def get_absolute_url(self):
        return reverse_lazy('units:detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Unit.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Unit, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')
