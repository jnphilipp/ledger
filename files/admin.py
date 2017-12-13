# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from files.models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name', 'file', 'uploader',
                           'content_type', 'object_id']}),
    ]
    list_display = ('name', 'uploader', 'updated_at')
    list_filter = ('content_type', 'uploader')
    ordering = ('name',)
    readonly_fields = ('slug',)
