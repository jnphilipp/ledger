from accounts.models import Account, Category, Entry, Tag, Unit, TextFieldSingleLine
from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput

import autocomplete_light

class AccountAdmin(admin.ModelAdmin):
	def get_ledgers(self, obj):
		return ', '.join([str(ledger) for ledger in obj.ledgers.all()])

	list_display = ('name', 'get_ledgers', 'balance', 'unit', 'updated_at')
	list_filter = ('unit', 'ledger')
	readonly_fields = ('slug',)
	search_fields = ('name', 'unit__name')
	get_ledgers.short_description = 'Ledgers'

	formfield_overrides = {
		TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
	}

	fieldsets = [
		(None, {'fields': ['ledgers', 'slug', 'name', 'balance', 'category', 'unit']}),
	]

	filter_horizontal = ('ledgers',)

class CategoryAdmin(admin.ModelAdmin):
	def get_queryset(self, request):
		return Category.objects.annotate(entry_count=Count('entry'))

	def show_entry_count(self, inst):
		return inst.entry_count

	list_display = ('name', 'show_entry_count', 'updated_at')
	readonly_fields = ('slug',)
	search_fields = ('name',)
	show_entry_count.admin_order_field = 'entry_count'
	show_entry_count.short_description = 'Number of Entries'

	formfield_overrides = {
		TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
	}

	fieldsets = [
		(None, {'fields': ['slug', 'name']}),
	]

class EntryAdmin(admin.ModelAdmin):
	def get_ledgers(self, obj):
		return ', '.join([str(ledger) for ledger in obj.account.ledgers.all()])

	list_display = ('account', 'get_ledgers', 'serial_number', 'day', 'category', 'additional')
	list_filter = ('account', 'category', 'day', 'tags')
	get_ledgers.short_description = 'Ledgers'

	formfield_overrides = {
		TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
	}

	fieldsets = [
		(None, {'fields': ['serial_number', 'day', 'amount', 'category', 'additional', 'tags']}),
	]

class TagAdmin(admin.ModelAdmin):
	def get_queryset(self, request):
		return Tag.objects.annotate(entry_count=Count('entries'))

	def show_entry_count(self, inst):
		return inst.entry_count

	list_display = ('name', 'show_entry_count', 'updated_at')
	readonly_fields = ('slug',)
	search_fields = ('name',)
	show_entry_count.admin_order_field = 'entry_count'
	show_entry_count.short_description = 'Number of Entries'

	formfield_overrides = {
		TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
	}

	fieldsets = [
		(None, {'fields': ['slug', 'name']}),
	]

class UnitAdmin(admin.ModelAdmin):
	list_display = ('name', 'symbol', 'updated_at')
	readonly_fields = ('slug',)
	search_fields = ('name', 'symbol')

	formfield_overrides = {
		TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
	}

	fieldsets = [
		(None, {'fields': ['slug', 'name', 'symbol']}),
	]

admin.site.register(Account, AccountAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Unit, UnitAdmin)