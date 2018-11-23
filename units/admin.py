# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name', 'symbol', 'precision']}),
    ]
    list_display = ('name', 'symbol', 'precision')
    readonly_fields = ('slug',)
    search_fields = ('name', 'symbol')
