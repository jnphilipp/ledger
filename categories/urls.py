# -*- coding: utf-8 -*-

from django.urls import path

from .views import category, tag
from .views.api import category as category_api
from .views.api import tag as tag_api
from .views.api.charts import category as category_chart
from .views.api.charts import tag as tag_chart


app_name = 'categories'
urlpatterns = [
    path('category/', category.list, name='categories'),
    path('category/add/', category.add, name='category_add'),
    path('category/add_another/', category.add_another,
         name='category_add_another'),
    path('category/<slug:slug>/', category.detail, name='category'),
    path('category/<slug:slug>/delete/', category.delete,
         name='category_delete'),
    path('category/<slug:slug>/edit/', category.edit, name='category_edit'),
    path('category/<slug:slug>/entries/', category.entries,
         name='category_entries'),
    path('category/<slug:slug>/statistics/', category.statistics,
         name='category_statistics'),

    path('tag/', tag.list, name='tags'),
    path('tag/add/', tag.add, name='tag_add'),
    path('tag/add_another/', tag.add_another, name='tag_add_another'),
    path('tag/<slug:slug>/', tag.detail, name='tag'),
    path('tag/<slug:slug>/edit/', tag.edit, name='tag_edit'),
    path('tag/<slug:slug>/delete/', tag.delete, name='tag_delete'),
    path('tag/<slug:slug>/entries/', tag.entries, name='tag_entries'),
    path('tag/<slug:slug>/statistics/', tag.statistics, name='tag_statistics'),

    path('api/category/autocomplete', category_api.autocomplete,
         name='category_autocomplete'),
    path('api/category/<slug:slug>/charts/statistics/',
         category_chart.statistics, name='category_chart_statistics'),
    path('api/tag/autocomplete', tag_api.autocomplete,
         name='tag_autocomplete'),
    path('api/tag/<slug:slug>/charts/statistics/accounts/', tag_chart.accounts,
         name='tag_chart_statistics_accounts'),
    path('api/tag/<slug:slug>/chart/statistics/categories/',
         tag_chart.categories, name='tag_chart_statistics_categories'),
]
