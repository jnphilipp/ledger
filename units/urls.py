# -*- coding: utf-8 -*-

from django.urls import path

from .views import unit
from .views.api import unit as unit_api


app_name = 'units'
urlpatterns = [
    path('unit/', unit.list, name='units'),
    path('unit/add/', unit.add, name='unit_add'),
    path('unit/add_another/', unit.add_another, name='unit_add_another'),
    path('unit/<slug:slug>/', unit.detail, name='unit'),
    path('unit/<slug:slug>/edit/', unit.edit, name='unit_edit'),

    path('api/unit/autocomplete/', unit_api.autocomplete,
         name='unit_autocomplete'),
]
