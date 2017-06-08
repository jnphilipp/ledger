# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify


class TextFieldSingleLine(models.TextField):
    pass


class Unit(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(max_length=2048, unique=True)
    name = TextFieldSingleLine(unique=True)
    symbol = TextFieldSingleLine(unique=True)
    precision = models.PositiveIntegerField(default=2)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Unit.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Unit, self).save(*args, **kwargs)

    def __str__(self):
        return self.name.lower()

    class Meta:
        ordering = ('name',)
        verbose_name = ' unit'
