from accounts.functions.dates import daterange
from accounts.models import Account, Category, Entry, Tag, Unit
from datetime import datetime
from django import forms
from django.contrib.admin import site, widgets
from django.db import models

import autocomplete_light

class AccountForm(autocomplete_light.ModelForm):
	class Meta:
		model = Account
		fields = ('name', 'category', 'unit')

	def __init__(self, *args, **kwargs):
		super(AccountForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})

class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ('name',)

	def __init__(self, *args, **kwargs):
		super(CategoryForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})

class EntryForm(autocomplete_light.ModelForm):
	class Meta:
		model = Entry
		exclude = ['serial_number', 'account']

	def __init__(self, *args, **kwargs):
		super(EntryForm, self).__init__(*args, **kwargs)
		self.fields['additional'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
		self.fields['day'].widget = forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'yyyy-mm-dd', 'class':'form-control'})
		self.fields['amount'].widget = forms.NumberInput(attrs={'step':'any', 'autocomplete':'off', 'class':'form-control'})

class StandingEntryForm(autocomplete_light.ModelForm):
	start_date = forms.CharField(widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'yyyy-mm-dd', 'class':'form-control'}))
	end_date = forms.CharField(widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'yyyy-mm-dd', 'class':'form-control'}))
	execution = forms.ChoiceField(choices=((1, 'monthly'), (2, 'quarterly'), (3, 'half-yearly'), (4, 'yearly')))

	class Meta:
		model = Entry
		exclude = ['serial_number', 'day', 'account']
		fields = ['start_date', 'end_date', 'execution', 'amount', 'category', 'additional', 'tags']

	def __init__(self, *args, **kwargs):
		super(StandingEntryForm, self).__init__(*args, **kwargs)
		self.fields['additional'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
		self.fields['amount'].widget = forms.NumberInput(attrs={'step':'none', 'autocomplete':'off', 'class':'form-control'})

	def save(self, commit=True):
		instance = super(StandingEntryForm, self).save(commit=False)
		entries = []
		start = datetime.strptime(self.cleaned_data['start_date'], '%Y-%m-%d').date()
		end = datetime.strptime(self.cleaned_data['end_date'], '%Y-%m-%d').date()
		for date in daterange(start, end, int(self.cleaned_data['execution'])):
			entry, created = Entry.objects.update_or_create(day=date, amount=instance.amount, category=instance.category, additional=instance.additional, account=instance.account)
			for tag in self.cleaned_data['tags']: entry.tags.add(tag)
			entries.append(entry)
		return entries

class TagForm(forms.ModelForm):
	class Meta:
		model = Tag
		fields = ('name',)

	def __init__(self, *args, **kwargs):
		super(TagForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})

class UnitForm(forms.ModelForm):
	class Meta:
		model = Unit
		fields = ('name','symbol')

	def __init__(self, *args, **kwargs):
		super(UnitForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
		self.fields['symbol'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})

class FilterForm(forms.Form):
	category = autocomplete_light.ChoiceField('CategoryFilter', required=False)
	tag = autocomplete_light.ChoiceField('TagFilter', required=False)