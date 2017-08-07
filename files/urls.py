# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^file/add/(?P<content_type>[\d]+)/(?P<object_id>[\d]+)/$', views.add, name='add'),
    url(r'^file/add_another/(?P<content_type>[\d]+)/(?P<object_id>[\d]+)/$', views.add_another, name='add_another'),
    url(r'^file/(?P<slug>[\w-]+)/$', views.detail, name='file'),
    url(r'^file/(?P<slug>[\w-]+)/edit/$', views.edit, name='edit'),
    url(r'^file/(?P<slug>[\w-]+)/delete/$', views.delete, name='delete'),
]
