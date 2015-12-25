# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models

class Ledger(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    accounts = models.ManyToManyField('accounts.Account')

    def __str__(self):
        return 'ledger-%s' % self.user

    class Meta:
        ordering = ('user',)

class Budget(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    income_tags = models.ManyToManyField('accounts.Tag', blank=True, related_name='income_tags')
    consumption_tags = models.ManyToManyField('accounts.Tag', blank=True, related_name='consumption_tags')
    insurance_tags = models.ManyToManyField('accounts.Tag', blank=True, related_name='insurance_tags')
    savings_tags = models.ManyToManyField('accounts.Tag', blank=True, related_name='savings_tags')

    def __str__(self):
        return 'budget-%s' % self.user

    class Meta:
        ordering = ('user',)
