# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UnitsConfig(AppConfig):
    name = 'units'
    verbose_name = _('Unit')
    verbose_name_plural = _('Units')
