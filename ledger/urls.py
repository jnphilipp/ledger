from accounts.models import Category, Tag
from accounts.forms import CategoryForm, TagForm
from django.conf import settings
from django.conf.urls import patterns, include, url

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.site.site_header = 'ledger administration'
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'accounts.views.account.dashboard', name='dashboard'),
	url(r'^accounts/account/add/$', 'accounts.views.account.add_account', name='add_account'),
	url(r'^accounts/account/(?P<slug>[\w-]+)/$', 'accounts.views.account.account', name='account'),
	url(r'^accounts/account/(?P<slug>[\w-]+)/entries/$', 'accounts.views.account.entries', name='account_entries'),
	url(r'^accounts/account/(?P<slug>[\w-]+)/entries/add/$', 'accounts.views.entry.add', name='entry_add'),
	url(r'^accounts/account/(?P<slug>[\w-]+)/entries/swap/$', 'accounts.views.entry.swap', name='entry_swap'),
	url(r'^accounts/account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/change/$', 'accounts.views.entry.change', name='entry_change'),
	url(r'^accounts/category/$', 'accounts.views.category.categories', name='categories'),
	url(r'^accounts/category/add_another/$', autocomplete_light.CreateView.as_view(model=Category, form_class=CategoryForm, template_name='ledger/accounts/category/add_another.html'), name='category_add_another_create'),
	url(r'^accounts/category/(?P<slug>[\w-]+)/$', 'accounts.views.category.category', name='category'),
	url(r'^accounts/category/(?P<slug>[\w-]+)/entries/$', 'accounts.views.category.entries', name='category_entries'),
	url(r'^accounts/tag/$', 'accounts.views.tag.tags', name='tags'),
	url(r'^accounts/tag/add_another/$', autocomplete_light.CreateView.as_view(model=Tag, form_class=TagForm, template_name='ledger/accounts/tag/add_another.html'), name='tag_add_another_create'),
	url(r'^accounts/tag/(?P<slug>[\w-]+)/$', 'accounts.views.tag.tag', name='tag'),
	url(r'^accounts/tag/(?P<slug>[\w-]+)/entries/$', 'accounts.views.tag.entries', name='tag_entries'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^autocomplete/', include('autocomplete_light.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	)