# -*- coding: utf-8 -*-

from django.urls import path

from . import views


app_name = 'units'
urlpatterns = [
    path('unit/', views.list, name='units'),
    path('unit/add/', views.add, name='unit_add'),
    path('unit/autocomplete/', views.autocomplete, name='unit_autocomplete'),
    path('unit/add_another/', views.add_another, name='unit_add_another'),
    path('unit/<slug:slug>/', views.detail, name='unit'),
    path('unit/<slug:slug>/edit/', views.edit, name='unit_edit'),
]
