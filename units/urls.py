# -*- coding: utf-8 -*-

from django.urls import path

from .views import *


app_name = 'units'
urlpatterns = [
    path('', ListView.as_view(), name='list'),
    path('add/', CreateView.as_view(), name='create'),
    path('add/another/', CreateView.as_view(), name='create_another'),
    path('autocomplete/', autocomplete, name='unit_autocomplete'),
    path('<slug:slug>/', DetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', UpdateView.as_view(), name='edit'),
]
