# -*- coding: utf-8 -*-

from django.conf.urls import url
# from .models import Category, Tag, Unit
# from .forms import CategoryForm, TagForm, UnitForm
from .views.account import account, entry, standing_entry#, budget, category, entry, standing_entry, statistics, tag
# from .views.api.accounts.charts import categories, statistics as acs, tags
# from .views.api.categories import charts
# from .views.api.statistics import charts as sc
# from .views.api.tags.charts import statistics as ts
from .views.api import account as account_api
from .views.api.account.charts import categories, tags

urlpatterns = [
    url(r'^account/$', account.accounts, name='accounts'),
    url(r'^account/add/$', account.add, name='account_add'),


    # url(r'^entry/$', entry.entries, name='entries'),
    # url(r'^account/entries/add/$', entry.add, name='entry_add'),
    # url(r'^account/entries/standing/add/$', standing_entry.add, name='standing_entry_add'),
    # url(r'^account/entries/(?P<entry_id>\d+)/change/$', entry.edit, name='entry_edit'),
    # url(r'^account/entries/(?P<entry_id>\d+)/delete/$', entry.delete, name='entry_delete'),
    # url(r'^account/entries/(?P<entry_id>\d+)/duplicate/$', entry.duplicate, name='entry_duplicate'),

    url(r'^account/(?P<slug>[\w-]+)/$', account.account, name='account'),
    url(r'^account/(?P<slug>[\w-]+)/edit/$', account.edit, name='account_edit'),
    url(r'^account/(?P<slug>[\w-]+)/delete/$', account.delete, name='account_delete'),
    url(r'^account/(?P<slug>[\w-]+)/entries/$', entry.entries, name='account_entries'),
    url(r'^account/(?P<slug>[\w-]+)/entries/add/$', entry.add, name='account_entry_add'),
    url(r'^account/(?P<slug>[\w-]+)/entries/standing/add/$', standing_entry.add, name='account_standing_entry_add'),
    url(r'^account/(?P<slug>[\w-]+)/entries/swap/(?P<e1>\d+)/(?P<e2>\d+)/$', entry.swap, name='account_entry_swap'),
    url(r'^account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)$', entry.entry, name='account_entry'),
    url(r'^account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/change/$', entry.edit, name='account_entry_edit'),
    url(r'^account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/delete/$', entry.delete, name='account_entry_delete'),
    url(r'^account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/duplicate/$', entry.duplicate, name='account_entry_duplicate'),
    url(r'^account/(?P<slug>[\w-]+)/statistics/$', account.statistics, name='account_statistics'),

    url(r'^api/account/autocomplete', account_api.autocomplete, name='account_autocomplete'),
    url(r'^api/account/(?P<slug>[\w-]+)/charts/categories/$', categories.categories, name='account_chart_categories'),
    url(r'^api/account/(?P<slug>[\w-]+)/charts/categories/statistics/$', categories.statistics, name='account_chart_categories_statistics'),
    url(r'^api/account/(?P<slug>[\w-]+)/charts/tags/$', tags.tags, name='account_chart_tags'),
    url(r'^api/account/(?P<slug>[\w-]+)/charts/tags/statistics/$', tags.statistics, name='account_chart_tags_statistics'),
]
