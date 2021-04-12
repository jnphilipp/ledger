# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LedgerConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = 'ledger'
    verbose_name = _('Ledger')
    verbose_name_plural = _('Ledgers')
