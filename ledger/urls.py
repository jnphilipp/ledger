# -*- coding: utf-8 -*-

from accounts.views import account
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views import generic, static

admin.site.site_header = 'ledger administration'

urlpatterns = [
    url(r'^$', account.dashboard, name='dashboard'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^profile/', include('app.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
]

if settings.DEBUG:
    urlpatterns += [url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT})]
