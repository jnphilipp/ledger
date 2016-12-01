# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import unit
from .views.api import unit as unit_api


urlpatterns = [
    url(r'^unit/$', unit.list, name='units'),
    url(r'^unit/add/$', unit.add, name='unit_add'),
    url(r'^unit/add_another/$', unit.add_another, name='unit_add_another'),
    url(r'^unit/(?P<slug>[\w-]+)/$', unit.detail, name='unit'),
    url(r'^unit/(?P<slug>[\w-]+)/edit/$', unit.edit, name='unit_edit'),

    url(r'api/unit/autocomplete', unit_api.autocomplete, name='unit_autocomplete'),
]
