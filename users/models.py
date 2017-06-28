# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Ledger(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    accounts = models.ManyToManyField('accounts.Account', blank=True, verbose_name=_('Accounts'))

    def __str__(self):
        return 'Ledger-%s' % self.user

    class Meta:
        ordering = ('user',)
        verbose_name = _('Ledger')
        verbose_name_plural = _('Ledgers')


class Budget(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    income_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='income_tags', verbose_name=_('Income tags'))
    consumption_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='consumption_tags', verbose_name=_('Consumption tags'))
    insurance_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='insurance_tags', verbose_name=_('Insurance tags'))
    savings_tags = models.ManyToManyField('categories.Tag', blank=True, related_name='savings_tags', verbose_name=_('Savings tags'))

    def __str__(self):
        return 'Budget-%s' % self.user

    class Meta:
        ordering = ('user',)
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')
