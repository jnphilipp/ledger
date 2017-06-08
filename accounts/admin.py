# -*- coding: utf-8 -*-

from accounts.models import Account, Entry, TextFieldSingleLine
from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput


class AccountAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Account.objects.annotate(entry_count=Count('entries'))

    def show_entry_count(self, inst):
        return inst.entry_count

    def get_ledgers(self, obj):
        return ', '.join([str(ledger) for ledger in obj.ledgers.all()])

    list_display = ('name', 'get_ledgers', 'show_entry_count', 'unit', 'updated_at')
    list_filter = ('unit', 'ledger')
    readonly_fields = ('slug',)
    search_fields = ('name', 'unit__name')
    show_entry_count.admin_order_field = 'entry_count'
    show_entry_count.short_description = 'Number of Entries'
    get_ledgers.short_description = 'Ledgers'

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete': 'off'})},
    }

    fieldsets = [
        (None, {'fields': ['ledgers', 'slug', 'name', 'category', 'unit']}),
    ]

    filter_horizontal = ('ledgers',)


class EntryAdmin(admin.ModelAdmin):
    list_display = ('account', 'serial_number', 'day', 'category', 'additional', 'updated_at')
    list_filter = ('account', 'category', 'day', 'tags')

    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete': 'off'})},
    }

    fieldsets = [
        (None, {'fields': ['serial_number', 'day', 'amount', 'category', 'additional', 'tags']}),
    ]


admin.site.register(Account, AccountAdmin)
admin.site.register(Entry, EntryAdmin)
