# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth import views as auth
from . import views


urlpatterns = [
    url(r'^profile/$', views.profile, name='profile'),

    url(r'^password/$', auth.password_change, name='password_change'),
    url(r'^password/done/$', auth.password_change_done, name='password_change_done'),
    url(r'^password/reset/$', views.password_reset, name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.password_reset_confirm, name='password_reset_confirm'),

    url(r'^signin/$', views.signin, name='signin'),
    url(r'^signout/$', auth.logout, name='signout'),
    url(r'^signup/$', views.signup, name='signup'),
]
