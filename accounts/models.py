# -*- coding: utf-8 -*-

from categories.models import Category, Tag
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from time import time
from units.models import Unit
from users.models import Ledger


class TextFieldSingleLine(models.TextField):
    pass


class Account(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(unique=True)
    name = TextFieldSingleLine()
    unit = models.ForeignKey(Unit)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='accounts', null=True)
    ledgers = models.ManyToManyField(Ledger, through=Ledger.accounts.through)


    def get_absolute_url(self):
        return reverse('account', args=[self.slug])


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) if not Account.objects.filter(slug=slugify(self.name)).exists() else slugify('%s%s' % (int(round(time() * 1000)), self.name))
        else:
            orig = Account.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name) if not Account.objects.filter(slug=slugify(self.name)).exists() else slugify('%s%s' % (int(round(time() * 1000)), self.name))
        super(Account, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


    class Meta:
        ordering = ('name',)
        verbose_name = ' account'
        verbose_name_plural = ' accounts'


class Entry(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='entries')
    serial_number = models.IntegerField()
    day = models.DateField()
    amount = models.FloatField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='entries')
    additional = TextFieldSingleLine(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='entries')


    def save(self, *args, **kwargs):
        move = False
        if self.id:
            orig = Entry.objects.get(id=self.id)
            entry = Entry.objects.filter(account=self.account).filter(day__lte=self.day).last()
            next_serial_number = entry.serial_number + 1 if entry else 1
            if orig.day != self.day and (orig.serial_number + 1) != next_serial_number:
                move = True
        if not self.id or move:
            if Entry.objects.filter(account=self.account).filter(day__lte=self.day).exists():
                next_serial_number = Entry.objects.filter(account=self.account).filter(day__lte=self.day).last().serial_number + 1
            else:
                next_serial_number = 1
            for entry in Entry.objects.filter(account=self.account).filter(serial_number__gte=next_serial_number).reverse():
                entry.serial_number += 1
                entry.save()
            self.serial_number = next_serial_number
        super(Entry, self).save()


    class Meta:
        ordering = ('account', 'serial_number')
        unique_together = ('account', 'serial_number')
        verbose_name = ' entry'
        verbose_name_plural = ' entries'
