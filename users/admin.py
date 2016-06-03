# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from users.models import Ledger


class LedgerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Ledger.objects.annotate(account_count=Count('accounts'))


    def show_account_count(self, inst):
        return inst.account_count


    list_display = ('user', 'show_account_count', 'updated_at')
    list_filter = ('user', 'accounts')
    search_fields = ('user', 'account__name')
    show_account_count.admin_order_field = 'account_count'
    show_account_count.short_description = 'Number of Accounts'

    fieldsets = [
        (None, {'fields': ['user', 'accounts']}),
    ]

    filter_horizontal = ('accounts',)


admin.site.register(Ledger, LedgerAdmin)
