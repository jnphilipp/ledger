# -*- coding: utf-8 -*-

from autocomplete_light import shortcuts as al
from django.conf.urls import url
from .models import Category, Tag, Unit
from .forms import CategoryForm, TagForm, UnitForm
from .views import account, category, entry, standing_entry, statistics, tag
from .views.api.accounts.charts import categories, statistics as acs, tags
from .views.api.categories import charts
from .views.api.statistics import charts as sc
from .views.api.tags.charts import statistics as ts

urlpatterns = [
    url(r'^account/$', account.dashboard, name='accounts'),
    url(r'^account/add/$', account.add, name='account_add'),
    url(r'^account/(?P<slug>[\w-]+)/$', account.account, name='account'),
    url(r'^account/(?P<slug>[\w-]+)/edit/$', account.edit, name='account_edit'),
    url(r'^account/(?P<slug>[\w-]+)/delete/$', account.delete, name='account_delete'),
    url(r'^account/(?P<slug>[\w-]+)/entries/$', account.entries, name='account_entries'),
    url(r'^account/(?P<slug>[\w-]+)/entries/add/$', entry.add, name='entry_add'),
    url(r'^account/(?P<slug>[\w-]+)/entries/standing/add/$', standing_entry.add, name='standing_entry_add'),
    url(r'^account/(?P<slug>[\w-]+)/entries/swap/$', entry.swap, name='entry_swap'),
    url(r'^account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/change/$', entry.edit, name='entry_edit'),
    url(r'^account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/delete/$', entry.delete, name='entry_delete'),
    url(r'^account/(?P<slug>[\w-]+)/entries/(?P<entry_id>\d+)/duplicate/$', entry.duplicate, name='entry_duplicate'),
    url(r'^account/(?P<slug>[\w-]+)/statistics/$', account.statistics, name='account_statistics'),
    url(r'^category/$', category.categories, name='categories'),
    url(r'^category/add_another/$', al.CreateView.as_view(model=Category, form_class=CategoryForm, template_name='ledger/accounts/category/add_another.html'), name='category_add_another_create'),
    url(r'^category/(?P<slug>[\w-]+)/$', category.category, name='category'),
    url(r'^category/(?P<slug>[\w-]+)/edit/$', category.edit, name='category_edit'),
    url(r'^category/(?P<slug>[\w-]+)/delete/$', category.delete, name='category_delete'),
    url(r'^category/(?P<slug>[\w-]+)/entries/$', category.entries, name='category_entries'),
    url(r'^category/(?P<slug>[\w-]+)/statistics/$', category.statistics, name='category_statistics'),
    url(r'^statistics/$', statistics.statistics, name='statistics'),
    url(r'^tag/$', tag.tags, name='tags'),
    url(r'^tag/add_another/$', al.CreateView.as_view(model=Tag, form_class=TagForm, template_name='ledger/accounts/tag/add_another.html'), name='tag_add_another_create'),
    url(r'^tag/(?P<slug>[\w-]+)/$', tag.tag, name='tag'),
    url(r'^tag/(?P<slug>[\w-]+)/edit/$', tag.edit, name='tag_edit'),
    url(r'^tag/(?P<slug>[\w-]+)/delete/$', tag.delete, name='tag_delete'),
    url(r'^tag/(?P<slug>[\w-]+)/entries/$', tag.entries, name='tag_entries'),
    url(r'^tag/(?P<slug>[\w-]+)/statistics/$', tag.statistics, name='tag_statistics'),
    url(r'^unit/add_another/$', al.CreateView.as_view(model=Unit, form_class=UnitForm, template_name='ledger/accounts/unit/add_another.html'), name='unit_add_another_create'),

    url(r'^api/account/(?P<slug>[\w-]+)/charts/statistics/categories/$', acs.categories, name='account_charts_statistics_categories'),
    url(r'^api/account/(?P<slug>[\w-]+)/charts/statistics/tags/$', acs.tags, name='account_charts_statistics_tags'),
    url(r'^api/account/(?P<slug>[\w-]+)/charts/categories/$', categories.categories, name='account_chart_categories'),
    url(r'^api/account/(?P<slug>[\w-]+)/charts/tags/$', tags.tags, name='account_chart_tags'),
    url(r'^api/category/(?P<slug>[\w-]+)/charts/statistics/$', charts.statistics, name='category_charts_statistics'),
    url(r'^api/statistics/charts/categories/$', sc.categories, name='statistics_chart_categories'),
    url(r'^api/statistics/charts/tags/$', sc.tags, name='statistics_chart_tags'),
    url(r'^api/tag/(?P<slug>[\w-]+)/charts/statistics/accounts/$', ts.accounts, name='tag_charts_statistics_accounts'),
    url(r'^api/tag/(?P<slug>[\w-]+)/charts/statistics/categories/$', ts.categories, name='tag_charts_statistics_categories'),
]
