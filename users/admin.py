# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from users.models import Budget, Ledger


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'income_tags', 'consumption_tags',
                           'insurance_tags', 'savings_tags']}),
    ]
    filter_horizontal = ('income_tags', 'consumption_tags', 'insurance_tags',
                         'savings_tags')
    list_display = ('user', 'updated_at')
    list_filter = ('user',)
    search_fields = ('user', 'income_tags__name', 'consumption_tags__name',
                     'insurance_tags__name', 'savings_tags__name')


@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Ledger.objects.annotate(account_count=Count('accounts'))

    def show_account_count(self, inst):
        return inst.account_count

    fieldsets = [
        (None, {'fields': ['user', 'accounts']}),
    ]
    filter_horizontal = ('accounts',)
    list_display = ('user', 'show_account_count', 'updated_at')
    list_filter = ('user', 'accounts')
    search_fields = ('user', 'account__name')
    show_account_count.admin_order_field = 'account_count'
    show_account_count.short_description = _('Number of Accounts')
