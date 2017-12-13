# -*- coding: utf-8 -*-

import os

from accounts.models import Account, Entry
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from ledger.fields import SingleLineTextField


def get_file_path(instance, filename):
    name = slugify(instance.name) + os.path.splitext(filename)[1]
    if instance.content_type == ContentType.objects.get_for_model(Account):
        return os.path.join('files', 'account', str(instance.object_id),
                            'statements', name)
    elif instance.content_type == ContentType.objects.get_for_model(Entry):
        return os.path.join('files', 'account',
                            str(instance.content_object.account.pk), 'entries',
                            str(instance.object_id), name)
    else:
        return os.path.join('files', str(instance.content_type.pk),
                            str(instance.object_id), name)


class File(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    slug = models.SlugField(
        max_length=1024,
        unique=True,
        verbose_name=_('Slug')
    )
    name = SingleLineTextField(
        verbose_name=_('Name')
    )
    file = models.FileField(
        upload_to=get_file_path,
        max_length=4096,
        verbose_name=_('File')
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_('User')
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    def get_absolute_url(self):
        return reverse('files:file', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify('%s %s %s' % (self.content_type.pk,
                                              self.object_id, self.name))
        else:
            orig = File.objects.get(pk=self.pk)
            if orig.name != self.name or \
                    orig.content_type != self.content_type or \
                    orig.object_id != self.object_id:
                self.slug = slugify('%s %s %s' % (self.content_type.pk,
                                                  self.object_id, self.name))
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('File')
        verbose_name_plural = _('Files')
