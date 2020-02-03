# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from files.models import Invoice, Statement


@receiver(pre_delete, sender=Invoice)
def delete_invoice_file(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
    except FileNotFoundError:
        pass


@receiver(pre_delete, sender=Statement)
def delete_statement_file(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
    except FileNotFoundError:
        pass
