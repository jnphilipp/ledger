# -*- coding: utf-8 -*-

from django.urls import path

from .views import account, entry, standing_entry, transfer


app_name = 'accounts'
urlpatterns = [
    path('account/', account.ListView.as_view(), name='account_list'),
    path('account/create/', account.CreateView.as_view(),
         name='account_create'),
    path('account/autocomplete/', account.autocomplete,
         name='account_autocomplete'),
    path('account/<slug:slug>/', account.DetailView.as_view(),
         name='account_detail'),
    path('account/<slug:slug>/categories/<int:categories_year>/',
         account.DetailView.as_view(), name='account_detail'),
    path('account/<slug:slug>/categories/<int:categories_year>/' +
         '<int:categories_month>/', account.DetailView.as_view(),
         name='account_detail'),
    path('account/<slug:slug>/tags/<int:tags_year>/',
         account.DetailView.as_view(), name='account_detail'),
    path('account/<slug:slug>/tags/<int:tags_year>/<int:tags_month>/',
         account.DetailView.as_view(), name='account_detail'),
    path('account/<slug:slug>)/charts/categories/', account.charts.categories,
         name='account_chart_categories'),
    path('account/<slug:slug>)/charts/statistics/categories/',
         account.charts.statistics.categories,
         name='account_chart_statistics_categories'),
    path('account/<slug:slug>)/charts/statistics/categories/<int:year>/',
         account.charts.statistics.categories,
         name='account_chart_statistics_categories'),
    path('account/<slug:slug>)/charts/statistics/categories/<int:year>/<int:' +
         'month>/', account.charts.statistics.categories,
         name='account_chart_statistics_categories'),
    path('account/<slug:slug>)/charts/statistics/tags/',
         account.charts.statistics.tags, name='account_chart_statistics_tags'),
    path('account/<slug:slug>)/charts/statistics/tags/<int:year>/',
         account.charts.statistics.tags, name='account_chart_statistics_tags'),
    path('account/<slug:slug>)/charts/statistics/tags/<int:year>/<int:month>/',
         account.charts.statistics.tags, name='account_chart_statistics_tags'),
    path('account/<slug:slug>)/charts/tags/', account.charts.tags,
         name='account_chart_tags'),
    path('account/<slug:slug>/edit/', account.UpdateView.as_view(),
         name='account_edit'),
    path('account/<slug:slug>/close/', account.CloseView.as_view(),
         name='account_close'),
    path('account/<slug:slug>/delete/', account.DeleteView.as_view(),
         name='account_delete'),

    path('', entry.ListView.as_view(), name='entry_list'),
    path('<int:page>/', entry.ListView.as_view()),

    path('entry/create/', entry.CreateView.as_view(), name='entry_create'),
    path('entry/standing/create/', standing_entry.CreateView.as_view(),
         name='standing_entry_create'),
    path('entry/transfer/create/', transfer.CreateView.as_view(),
         name='transfer_create'),
    path('entry/<int:pk>/', entry.DetailView.as_view(),
         name='entry_detail'),
    path('entry/<int:pk>/edit/', entry.UpdateView.as_view(),
         name='entry_edit'),
    path('entry/<int:pk>/delete/', entry.DeleteView.as_view(),
         name='entry_delete'),
    path('entry/<int:pk>/duplicate/', entry.DuplicateView.as_view(),
         name='entry_duplicate'),
    path('entry/<int:pk>/swap/<str:direction>/', entry.SwapView.as_view(),
         name='entry_swap'),
]
