from accounts.models import Account, Category, Entry, Tag, Unit, TextFieldSingleLine
from django.contrib import admin
from django.forms import TextInput

import autocomplete_light

class AccountAdmin(admin.ModelAdmin):
	list_display = ('name', 'balance', 'unit', 'updated_at')
	list_filter = ('unit', 'ledger')
	readonly_fields = ('slug',)
	search_fields = ('name', 'unit__name')

	formfield_overrides = {
		TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
	}

	fieldsets = [
		(None, {'fields': ['ledgers', 'slug', 'name', 'balance', 'unit']}),
	]

	filter_horizontal = ('ledgers',)

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

class EntryAdmin(admin.ModelAdmin):
	list_display = ('account', 'serial_number', 'day', 'category', 'additional')
	list_filter = ('account', 'category', 'day', 'tags')

	formfield_overrides = {
		TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
	}

	fieldsets = [
		(None, {'fields': ['serial_number', 'day', 'amount', 'category', 'additional', 'tags']}),
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