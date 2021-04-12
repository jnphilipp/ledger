# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = 'accounts'
    verbose_name = _('Account')
    verbose_name_plural = _('Accounts')
