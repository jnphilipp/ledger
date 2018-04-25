# -*- coding: utf-8 -*-

from django.urls import path

from .views import category, tag


app_name = 'categories'
urlpatterns = [
    path('category/', category.list, name='categories'),
    path('category/add/', category.add, name='category_add'),
    path('category/add_another/', category.add_another,
         name='category_add_another'),
    path('category/autocomplete/', category.autocomplete,
         name='category_autocomplete'),
    path('category/<slug:slug>/', category.detail, name='category'),
    path('category/<slug:slug>/delete/', category.delete,
         name='category_delete'),
    path('category/<slug:slug>/edit/', category.edit, name='category_edit'),
    path('category/<slug:slug>/entries/', category.entries,
         name='category_entries'),
    path('category/<slug:slug>/statistics/', category.statistics,
         name='category_statistics'),
    path('category/<slug:slug>/statistics/charts/', category.charts.statistics,
         name='category_chart_statistics'),

    path('tag/', tag.list, name='tags'),
    path('tag/add/', tag.add, name='tag_add'),
    path('tag/add_another/', tag.add_another, name='tag_add_another'),
    path('tag/autocomplete/', tag.autocomplete, name='tag_autocomplete'),
    path('tag/<slug:slug>/', tag.detail, name='tag'),
    path('tag/<slug:slug>/edit/', tag.edit, name='tag_edit'),
    path('tag/<slug:slug>/delete/', tag.delete, name='tag_delete'),
    path('tag/<slug:slug>/entries/', tag.entries, name='tag_entries'),
    path('tag/<slug:slug>/statistics/', tag.statistics, name='tag_statistics'),
    path('tag/<slug:slug>/statistics/charts/accounts/', tag.charts.accounts,
         name='tag_chart_statistics_accounts'),
    path('tag/<slug:slug>/statistics/chart/categories/', tag.charts.categories,
         name='tag_chart_statistics_categories'),
]
