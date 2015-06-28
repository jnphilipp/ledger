from app.models import Ledger
from django.contrib import admin

import autocomplete_light

class LedgerAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    list_filter = ('user', 'accounts')
    search_fields = ('user', 'account__name')

    fieldsets = [
        (None, {'fields': ['user', 'accounts']}),
    ]

    filter_horizontal = ('accounts',)

admin.site.register(Ledger, LedgerAdmin)