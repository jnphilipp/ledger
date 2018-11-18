# -*- coding: utf-8 -*-

from django.urls import path

from .views import account, entry, standing_entry
from .views.api import account as account_api
from .views.api.account.charts import categories, tags


app_name = 'accounts'
urlpatterns = [
    path('account/', account.ListView.as_view(), name='account_list'),
    path('account/create/', account.CreateView.as_view(),
         name='account_create'),
    path('account/<slug:slug>/', account.DetailView.as_view(),
         name='account_detail'),
    path('account/<slug:slug>/edit/', account.edit, name='account_edit'),
    path('account/<slug:slug>/close/', account.close, name='account_close'),
    path('account/<slug:slug>/delete/', account.delete, name='account_delete'),
    path('account/<slug:slug>/entries/', entry.ListView.as_view(),
         name='account_entry_list'),
    path('account/<slug:slug>/entries/<int:page>/', entry.ListView.as_view()),
    path('account/<slug:slug>/entries/add/', entry.add,
         name='account_entry_add'),
    path('account/<slug:slug>/entries/standing/add/', standing_entry.add,
         name='account_standing_entry_add'),
    path('account/<slug:slug>/entries/swap/<int:e1>/<int:e2>/', entry.swap,
         name='account_entry_swap'),
    path('account/<slug:slug>/entry/<int:pk>/',
         entry.DetailView.as_view(), name='account_entry_detail'),
    path('account/<slug:slug>/entry/<int:pk>/change/', entry.edit,
         name='account_entry_edit'),
    path('account/<slug:slug>/entry/<int:pk>/delete/', entry.delete,
         name='account_entry_delete'),
    path('account/<slug:slug>/entry/<int:pk>/duplicate/',
         entry.duplicate, name='account_entry_duplicate'),
    path('account/<slug:slug>/statements/', account.DetailView.as_view(),
         name='account_statement_list'),
    path('account/<slug:slug>/statistics/', account.statistics,
         name='account_statistics'),

    path('entry/', entry.ListView.as_view(), name='entry_list'),
    path('entry/add/', entry.add, name='entry_add'),
    path('entry/standing/add/', standing_entry.add, name='standing_entry_add'),
    path('entry/<int:pk>/', entry.DetailView.as_view(),
         name='entry_detail'),
    path('entry/<int:pk>/change/', entry.edit, name='entry_edit'),
    path('entry/<int:pk>/delete/', entry.delete, name='entry_delete'),
    path('entry/<int:pk>/duplicate/', entry.duplicate,
         name='entry_duplicate'),

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
