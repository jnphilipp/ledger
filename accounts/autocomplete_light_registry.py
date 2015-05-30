from accounts.models import Account, Category, Tag, Unit
from django.db.models import Q

import autocomplete_light

class Autocomplete(autocomplete_light.AutocompleteModelBase):
	search_fields=['name']
	attrs={
		'placeholder': 'filter',
		'data-autocomplete-minimum-characters': 1,
	}
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	}

	def choice_html(self, choice):
		return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice).lower())

autocomplete_light.register(Account, Autocomplete)
autocomplete_light.register(Unit, Autocomplete, add_another_url_name='unit_add_another_create')

class CategoryAutocomplete(autocomplete_light.AutocompleteModelBase):
	search_fields=['name']
	attrs={
		'placeholder': 'filter',
		'data-autocomplete-minimum-characters': 1,
	}
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	}

	def choices_for_request(self):
		self.choices = self.choices.filter(Q(entry__account__ledger__user=self.request.user) | Q(account__ledger__user=self.request.user)).distinct()
		return super(CategoryAutocomplete, self).choices_for_request()

	def choice_html(self, choice):
		return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice).lower())
autocomplete_light.register(Category, CategoryAutocomplete, add_another_url_name='category_add_another_create')

class TagAutocomplete(autocomplete_light.AutocompleteModelBase):
	search_fields=['name']
	attrs={
		'placeholder': 'filter',
		'data-autocomplete-minimum-characters': 1,
	}
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	}

	def choices_for_request(self):
		self.choices = self.choices.filter(entries__account__ledger__user=self.request.user).distinct()
		return super(TagAutocomplete, self).choices_for_request()

	def choice_html(self, choice):
		return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice).lower())
autocomplete_light.register(Tag, TagAutocomplete, add_another_url_name='tag_add_another_create')

class CategoryFilter(autocomplete_light.AutocompleteModelBase):
	search_fields=['name']
	attrs={
		'data-autocomplete-minimum-characters': 1,
	}
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	}

	def choices_for_request(self):
		self.choices = self.choices.filter(Q(entry__account__ledger__user=self.request.user) | Q(account__ledger__user=self.request.user)).distinct()
		return super(CategoryFilter, self).choices_for_request()

	def choice_html(self, choice):
		return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice).lower())
autocomplete_light.register(Category, CategoryFilter, attrs={'placeholder': 'category'})
autocomplete_light.register(Category, CategoryFilter, name='CategoriesFilter', attrs={'placeholder': 'categories'})

class TagFilter(autocomplete_light.AutocompleteModelBase):
	search_fields=['name']
	attrs={
		'data-autocomplete-minimum-characters': 1,
	}
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	}

	def choices_for_request(self):
		self.choices = self.choices.filter(entries__account__ledger__user=self.request.user).distinct()
		return super(TagFilter, self).choices_for_request()

	def choice_html(self, choice):
		return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice).lower())
autocomplete_light.register(Tag, TagFilter, attrs={'placeholder': 'tag'})
autocomplete_light.register(Tag, TagFilter, name='TagsFilter', attrs={'placeholder': 'tags'})