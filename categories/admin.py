# -*- coding: utf-8 -*-

from categories.models import Category, Tag, TextFieldSingleLine
from django.contrib import admin
from django.forms import TextInput


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
    ]


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
    ]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
