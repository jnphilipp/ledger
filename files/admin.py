# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import TextInput
from files.models import File, TextFieldSingleLine


class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploader', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('slug',)

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete': 'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'name', 'file', 'uploader', 'content_type', 'object_id']}),
    ]


admin.site.register(File, FileAdmin)
