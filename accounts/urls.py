# -*- coding: utf-8 -*-

from django.urls import path

from .views import account, entry, standing_entry
from .views.api import account as account_api
from .views.api.account.charts import categories, tags


app_name = 'accounts'
urlpatterns = [
    path('account/', account.list, name='accounts'),
    path('account/add/', account.add, name='account_add'),

    path('entry/', entry.list, name='entries'),
    path('entry/add/', entry.add, name='entry_add'),
    path('entry/standing/add/', standing_entry.add, name='standing_entry_add'),
    path('entry/<int:entry_id>/', entry.detail, name='entry'),
    path('entry/<int:entry_id>/change/', entry.edit, name='entry_edit'),
    path('entry/<int:entry_id>/delete/', entry.delete, name='entry_delete'),
    path('entry/<int:entry_id>/duplicate/', entry.duplicate,
         name='entry_duplicate'),

    path('account/<slug:slug>/', account.detail, name='account'),
    path('account/<slug:slug>/edit/', account.edit, name='account_edit'),
    path('account/<slug:slug>/close/', account.close, name='account_close'),
    path('account/<slug:slug>/delete/', account.delete, name='account_delete'),
    path('account/<slug:slug>/entries/', entry.list, name='account_entries'),
    path('account/<slug:slug>/entries/add/', entry.add,
         name='account_entry_add'),
    path('account/<slug:slug>/entries/standing/add/', standing_entry.add,
         name='account_standing_entry_add'),
    path('account/<slug:slug>/entries/swap/<int:e1>/<int:e2>/', entry.swap,
         name='account_entry_swap'),
    path('account/<slug:slug>/entries/<int:entry_id>/', entry.detail,
         name='account_entry'),
    path('account/<slug:slug>/entries/<int:entry_id>/change/', entry.edit,
         name='account_entry_edit'),
    path('account/<slug:slug>/entries/<int:entry_id>/delete/', entry.delete,
         name='account_entry_delete'),
    path('account/<slug:slug>/entries/<int:entry_id>/duplicate/',
         entry.duplicate, name='account_entry_duplicate'),
    path('account/<slug:slug>/statements/', account.statements,
         name='account_statements'),
    path('account/<slug:slug>/statistics/', account.statistics,
         name='account_statistics'),

    path('api/account/autocomplete', account_api.autocomplete,
         name='account_autocomplete'),
    path('api/account/<slug:slug>)/charts/categories/', categories.categories,
         name='account_chart_categories'),
    path('api/account/<slug:slug>)/charts/categories/statistics/',
         categories.statistics, name='account_chart_categories_statistics'),
    path('api/account/<slug:slug>)/charts/tags/', tags.tags,
         name='account_chart_tags'),
    path('api/account/<slug:slug>)/charts/tags/statistics/', tags.statistics,
         name='account_chart_tags_statistics'),
]
