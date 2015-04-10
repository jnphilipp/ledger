from accounts.models import Account, Category, Tag, Unit

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
autocomplete_light.register(Category, Autocomplete, add_another_url_name='category_add_another_create')
autocomplete_light.register(Tag, Autocomplete, add_another_url_name='tag_add_another_create')
autocomplete_light.register(Unit, Autocomplete, add_another_url_name='unit_add_another_create')

class Filter(autocomplete_light.AutocompleteModelBase):
	search_fields=['name']
	attrs={
		'data-autocomplete-minimum-characters': 1,
	}
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	}

	def choice_html(self, choice):
		return self.choice_html_format % (self.choice_value(choice), self.choice_label(choice).lower())

autocomplete_light.register(Category, Filter, attrs={'placeholder': 'category'})
autocomplete_light.register(Tag, Filter, attrs={'placeholder': 'tag'})