# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import category, tag
from .views.api import category as category_api
from .views.api import tag as tag_api
from .views.api.charts import category as category_chart
from .views.api.charts import tag as tag_chart


urlpatterns = [
    url(r'^category/$', category.list, name='categories'),
    url(r'^category/add/$', category.add, name='category_add'),
    url(r'^category/add_another/$', category.add_another, name='category_add_another'),
    url(r'^category/(?P<slug>[\w-]+)/$', category.detail, name='category'),
    url(r'^category/(?P<slug>[\w-]+)/edit/$', category.edit, name='category_edit'),
    url(r'^category/(?P<slug>[\w-]+)/delete/$', category.delete, name='category_delete'),
    url(r'^category/(?P<slug>[\w-]+)/entries/$', category.entries, name='category_entries'),
    url(r'^category/(?P<slug>[\w-]+)/statistics/$', category.statistics, name='category_statistics'),

    url(r'^tag/$', tag.list, name='tags'),
    url(r'^tag/add/$', tag.add, name='tag_add'),
    url(r'^tag/add_another/$', tag.add_another, name='tag_add_another'),
    url(r'^tag/(?P<slug>[\w-]+)/$', tag.detail, name='tag'),
    url(r'^tag/(?P<slug>[\w-]+)/edit/$', tag.edit, name='tag_edit'),
    url(r'^tag/(?P<slug>[\w-]+)/delete/$', tag.delete, name='tag_delete'),
    url(r'^tag/(?P<slug>[\w-]+)/entries/$', tag.entries, name='tag_entries'),
    url(r'^tag/(?P<slug>[\w-]+)/statistics/$', tag.statistics, name='tag_statistics'),

    url(r'^api/category/autocomplete', category_api.autocomplete, name='category_autocomplete'),
    url(r'^api/category/(?P<slug>[\w-]+)/charts/statistics/$', category_chart.statistics, name='category_chart_statistics'),
    url(r'^api/tag/autocomplete', tag_api.autocomplete, name='tag_autocomplete'),
    url(r'^api/tag/(?P<slug>[\w-]+)/charts/statistics/accounts/$', tag_chart.accounts, name='tag_chart_statistics_accounts'),
    url(r'^api/tag/(?P<slug>[\w-]+)/chart/statistics/categories/$', tag_chart.categories, name='tag_chart_statistics_categories'),
]
