# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CategoriesConfig(AppConfig):
    name = 'categories'
    verbose_name = _('Category')
    verbose_name_plural = _('Categories')
