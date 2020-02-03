# -*- coding: utf-8 -*-

from django.contrib import admin
from files.models import Invoice, Statement


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name', 'file', 'uploader', 'entry']}),
    ]
    list_display = ('name', 'entry', 'uploader', 'updated_at')
    list_filter = ('entry', 'uploader')
    ordering = ('name',)
    readonly_fields = ('slug',)


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name', 'file', 'uploader', 'account']}),
    ]
    list_display = ('name', 'account', 'uploader', 'updated_at')
    list_filter = ('account', 'uploader')
    ordering = ('name',)
    readonly_fields = ('slug',)
