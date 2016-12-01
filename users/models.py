# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models


class Ledger(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    accounts = models.ManyToManyField('accounts.Account', blank=True)


    def __str__(self):
        return '%s_ledger' % self.user


    class Meta:
        ordering = ('user',)
        verbose_name = ' ledger'
        verbose_name_plural = ' ledgers'


class Budget(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    income_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='income_tags')
    consumption_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='consumption_tags')
    insurance_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='insurance_tags')
    savings_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='savings_tags')


    def __str__(self):
        return 'budget-%s' % self.user


    class Meta:
        ordering = ('user',)
        verbose_name = ' budget'
        verbose_name_plural = ' budgets'