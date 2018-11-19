# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from files.models import File


@receiver(pre_delete, sender=File)
def delete_files(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
    except FileNotFoundError:
        pass
