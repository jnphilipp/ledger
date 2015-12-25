# -*- coding: utf-8 -*-

from app.models import Budget, Ledger
from django.contrib import admin

class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    list_filter = ('user', 'income_tags')
    search_fields = ('user', 'income_tags__name', 'consumption_tags__name', 'insurance_tags__name', 'savings_tags__name')

    fieldsets = [
        (None, {'fields': ['user', 'income_tags', 'consumption_tags', 'insurance_tags', 'savings_tags']}),
    ]

    filter_horizontal = ('income_tags', 'consumption_tags', 'insurance_tags', 'savings_tags')

class LedgerAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    list_filter = ('user', 'accounts')
    search_fields = ('user', 'account__name')

    fieldsets = [
        (None, {'fields': ['user', 'accounts']}),
    ]

    filter_horizontal = ('accounts',)

admin.site.register(Budget, BudgetAdmin)
admin.site.register(Ledger, LedgerAdmin)
