# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth import views
from .views import base, profile

urlpatterns = [
    url(r'^$', profile.profile, name='profile'),
    url(r'^password/$', views.password_change, name='password_change'),
    url(r'^password/done/$', views.password_change_done, name='password_change_done'),
    url(r'^password/reset/$', base.password_reset, name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', base.password_reset_confirm, name='password_reset_confirm'),
    url(r'^signin/$', base.signin, name='signin'),
    url(r'^signout/$', views.logout, name='signout'),
]
