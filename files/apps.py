# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = 'files'
    verbose_name = _('File')
    verbose_name_plural = _('Files')

    def ready(self):
        import files.signals
