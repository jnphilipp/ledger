# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = 'users'
    verbose_name = _('User')
    verbose_name_plural = _('Users')
