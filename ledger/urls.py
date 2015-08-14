from accounts.models import Category, Tag, Unit
from accounts.forms import CategoryForm, TagForm, UnitForm
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views import generic

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.site.site_header = 'ledger administration'
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'accounts.views.account.dashboard', name='dashboard'),
    url(r'^accounts/account/$', 'accounts.views.account.dashboard', name='accounts'),
    url(r'^accounts/account/add/$', 'accounts.views.account.add', name='account_add'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/$', 'accounts.views.account.account', name='account'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/edit/$', 'accounts.views.account.edit', name='account_edit'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/delete/$', 'accounts.views.account.delete', name='account_delete'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/entries/$', 'accounts.views.account.entries', name='account_entries'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/entries/add/$', 'accounts.views.entry.add', name='entry_add'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/entries/standing/add/$', 'accounts.views.standing_entry.add', name='standing_entry_add'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/entries/swap/$', 'accounts.views.entry.swap', name='entry_swap'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/change/$', 'accounts.views.entry.edit', name='entry_edit'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/delete/$', 'accounts.views.entry.delete', name='entry_delete'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/duplicate/$', 'accounts.views.entry.duplicate', name='entry_duplicate'),
    url(r'^accounts/account/(?P<slug>[\w-]+)/statistics/$', 'accounts.views.account.statistics', name='account_statistics'),
    url(r'^accounts/category/$', 'accounts.views.category.categories', name='categories'),
    url(r'^accounts/category/add_another/$', autocomplete_light.CreateView.as_view(model=Category, form_class=CategoryForm, template_name='ledger/accounts/category/add_another.html'), name='category_add_another_create'),
    url(r'^accounts/category/(?P<slug>[\w-]+)/$', 'accounts.views.category.category', name='category'),
    url(r'^accounts/category/(?P<slug>[\w-]+)/edit/$', 'accounts.views.category.edit', name='category_edit'),
    url(r'^accounts/category/(?P<slug>[\w-]+)/delete/$', 'accounts.views.category.delete', name='category_delete'),
    url(r'^accounts/category/(?P<slug>[\w-]+)/entries/$', 'accounts.views.category.entries', name='category_entries'),
    url(r'^accounts/category/(?P<slug>[\w-]+)/statistics/$', 'accounts.views.category.statistics', name='category_statistics'),
    url(r'^accounts/tag/$', 'accounts.views.tag.tags', name='tags'),
    url(r'^accounts/tag/add_another/$', autocomplete_light.CreateView.as_view(model=Tag, form_class=TagForm, template_name='ledger/accounts/tag/add_another.html'), name='tag_add_another_create'),
    url(r'^accounts/tag/(?P<slug>[\w-]+)/$', 'accounts.views.tag.tag', name='tag'),
    url(r'^accounts/tag/(?P<slug>[\w-]+)/edit/$', 'accounts.views.tag.edit', name='tag_edit'),
    url(r'^accounts/tag/(?P<slug>[\w-]+)/delete/$', 'accounts.views.tag.delete', name='tag_delete'),
    url(r'^accounts/tag/(?P<slug>[\w-]+)/entries/$', 'accounts.views.tag.entries', name='tag_entries'),
    url(r'^accounts/tag/(?P<slug>[\w-]+)/statistics/$', 'accounts.views.tag.statistics', name='tag_statistics'),
    url(r'^accounts/unit/add_another/$', autocomplete_light.CreateView.as_view(model=Unit, form_class=UnitForm, template_name='ledger/accounts/unit/add_another.html'), name='unit_add_another_create'),
    url(r'^accounts/statistics/$', 'accounts.views.statistics.statistics', name='statistics'),

    url(r'^api/accounts/account/(?P<slug>[\w-]+)/charts/statistics/categories/$', 'accounts.views.api.accounts.charts.statistics.categories', name='account_charts_statistics_categories'),
    url(r'^api/accounts/account/(?P<slug>[\w-]+)/charts/statistics/tags/$', 'accounts.views.api.accounts.charts.statistics.tags', name='account_charts_statistics_tags'),
    url(r'^api/accounts/account/(?P<slug>[\w-]+)/charts/categories/$', 'accounts.views.api.accounts.charts.categories.categories', name='account_chart_categories'),
    url(r'^api/accounts/account/(?P<slug>[\w-]+)/charts/tags/$', 'accounts.views.api.accounts.charts.tags.tags', name='account_chart_tags'),
    url(r'^api/accounts/category/(?P<slug>[\w-]+)/charts/statistics/$', 'accounts.views.api.categories.charts.statistics', name='category_charts_statistics'),
    url(r'^api/accounts/tag/(?P<slug>[\w-]+)/charts/statistics/accounts/$', 'accounts.views.api.tags.charts.statistics.accounts', name='tag_charts_statistics_accounts'),
    url(r'^api/accounts/tag/(?P<slug>[\w-]+)/charts/statistics/categories/$', 'accounts.views.api.tags.charts.statistics.categories', name='tag_charts_statistics_categories'),
    url(r'^api/statistics/charts/categories/$', 'accounts.views.api.statistics.charts.categories', name='statistics_chart_categories'),
    url(r'^api/statistics/charts/tags/$', 'accounts.views.api.statistics.charts.tags', name='statistics_chart_tags'),

    url(r'^profile/$', 'app.views.profile.profile', name='profile'),
    url(r'^profile/password/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^profile/password/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^profile/password/reset/$', 'app.views.base.password_reset', name='password_reset'),
    url(r'^profile/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'app.views.base.password_reset_confirm', name='password_reset_confirm'),
    url(r'^profile/signin/$', 'app.views.base.signin', name='signin'),
    url(r'^profile/signout/$', 'django.contrib.auth.views.logout', name='signout'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
