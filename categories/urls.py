# -*- coding: utf-8 -*-

from django.urls import path

from .views import category, tag


app_name = 'categories'
urlpatterns = [
    path('category/', category.ListView.as_view(), name='category_list'),
    path('category/autocomplete/', category.autocomplete,
         name='category_autocomplete'),
    path('category/<slug:slug>/', category.DetailView.as_view(),
         name='category_detail'),
    path('category/<slug:slug>/<int:year>/', category.DetailView.as_view(),
         name='category_detail'),
    path('category/<slug:slug>/charts/statistics/', category.charts.statistics,
         name='category_chart_statistics'),
    path('category/<slug:slug>/charts/statistics/<int:year>/',
         category.charts.statistics, name='category_chart_statistics'),
    path('category/<slug:slug>/delete/', category.DeleteView.as_view(),
         name='category_delete'),
    path('category/<slug:slug>/edit/', category.UpdateView.as_view(),
         name='category_edit'),

    path('tag/', tag.ListView.as_view(), name='tag_list'),
    path('tag/autocomplete/', tag.autocomplete, name='tag_autocomplete'),
    path('tag/<slug:slug>/', tag.DetailView.as_view(), name='tag_detail'),
    path('tag/<slug:slug>/<int:year>/', tag.DetailView.as_view(),
         name='tag_detail'),
    path('tag/<slug:slug>/charts/statistics/', tag.charts.statistics,
         name='tag_chart_statistics'),
    path('tag/<slug:slug>/charts/statistics/<int:year>/',
         tag.charts.statistics, name='tag_chart_statistics'),
    path('tag/<slug:slug>/edit/', tag.UpdateView.as_view(), name='tag_edit'),
    path('tag/<slug:slug>/delete/', tag.DeleteView.as_view(),
         name='tag_delete'),
]
