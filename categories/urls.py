# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import category, tag
from .views.api import category as category_api


urlpatterns = [
    url(r'^category/$', category.categories, name='categories'),
    url(r'^category/add/$', category.add, name='category_add'),
    url(r'^category/add_another/$', category.add_another, name='category_add_another'),
    url(r'^category/(?P<slug>[\w-]+)/$', category.category, name='category'),
    url(r'^category/(?P<slug>[\w-]+)/edit/$', category.edit, name='category_edit'),
    url(r'^category/(?P<slug>[\w-]+)/delete/$', category.delete, name='category_delete'),

    url(r'^tag/$', tag.tags, name='tags'),
    url(r'^tag/(?P<slug>[\w-]+)/$', tag.tag, name='tag'),
    url(r'^tag/(?P<slug>[\w-]+)/edit/$', tag.edit, name='tag_edit'),
    url(r'^tag/(?P<slug>[\w-]+)/delete/$', tag.delete, name='tag_delete'),

    url(r'api/category/autocomplete', category_api.autocomplete, name='category_autocomplete'),
]
