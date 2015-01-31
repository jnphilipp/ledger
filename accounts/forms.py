from accounts.models import Account, Category, Entry, Tag, Unit
from django import forms
from django.contrib.admin import site, widgets
from django.db import models

import autocomplete_light

class AccountForm(autocomplete_light.ModelForm):
	class Meta:
		model = Account
		fields = ('name','unit')

	def __init__(self, *args, **kwargs):
		super(AccountForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off'})

class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ('name',)

	def __init__(self, *args, **kwargs):
		super(CategoryForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off'})

class EntryForm(autocomplete_light.ModelForm):
	class Meta:
		model = Entry
		exclude = ['serial_number', 'account']

	def __init__(self, *args, **kwargs):
		super(EntryForm, self).__init__(*args, **kwargs)
		self.fields['additional'].widget = forms.TextInput(attrs={'autocomplete':'off'})
		self.fields['day'].widget = forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'yyyy-mm-dd'})
		self.fields['amount'].widget = forms.NumberInput(attrs={'step':'any', 'autocomplete':'off'})

class TagForm(forms.ModelForm):
	class Meta:
		model = Tag
		fields = ('name',)

	def __init__(self, *args, **kwargs):
		super(TagForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off'})

class UnitForm(forms.ModelForm):
	class Meta:
		model = Unit
		fields = ('name','symbol')

	def __init__(self, *args, **kwargs):
		super(UnitForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off'})
		self.fields['symbol'].widget = forms.TextInput(attrs={'autocomplete':'off'})