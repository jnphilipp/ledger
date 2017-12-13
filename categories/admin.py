# -*- coding: utf-8 -*-

from categories.models import Category, Tag
from django.contrib import admin
from django.forms import TextInput


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
    ]
    list_display = ('name', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
    ]
    list_display = ('name', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)
