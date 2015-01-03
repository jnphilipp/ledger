from accounts.models import Account, Category, Tag, Unit

import autocomplete_light

autocomplete_light.register(Account,
	search_fields=['name'],
	attrs={
		'placeholder': 'Filter',
		'data-autocomplete-minimum-characters': 1,
	},
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	},
)

autocomplete_light.register(Category,
	search_fields=['name'],
	attrs={
		'placeholder': 'Filter',
		'data-autocomplete-minimum-characters': 1,
	},
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	},
	add_another_url_name='category_add_another_create',
)

autocomplete_light.register(Tag,
	search_fields=['name'],
	attrs={
		'placeholder': 'Filter',
		'data-autocomplete-minimum-characters': 1,
	},
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	},
	add_another_url_name='tag_add_another_create',
)

autocomplete_light.register(Unit,
	search_fields=['name'],
	attrs={
		'placeholder': 'Filter',
		'data-autocomplete-minimum-characters': 1,
	},
	widget_attrs={
		'data-widget-maximum-values': 6,
		'class': 'modern-style',
	},
)