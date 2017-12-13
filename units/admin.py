# -*- coding: utf-8 -*-

from units.models import Unit
from django.contrib import admin
from django.forms import TextInput


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name', 'symbol', 'precision']}),
    ]
    list_display = ('name', 'symbol', 'precision')
    readonly_fields = ('slug',)
    search_fields = ('name', 'symbol')
