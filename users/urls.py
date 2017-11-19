# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views
from .views import budget
from .views.api import statistics


urlpatterns = [
    url(r'^$', views.profile, name='users'),
    url(r'^profile/$', views.profile, name='profile'),

    url(r'^budget/$', budget.budget, name='budget'),
    url(r'^budget/edit/$', budget.edit, name='budget_edit'),
    url(r'^statistics/$', views.statistics, name='statistics'),

    url(r'^password/$', views.password_change, name='password_change'),
    url(r'^password/done/$', views.password_change_done, name='password_change_done'),
    url(r'^password/reset/$', views.password_reset, name='password_reset'),
    url(r'^password/reset/done/$', views.password_reset_done, name='password_reset_done'),
    url(r'^password/reset/complete/$', views.password_reset_complete, name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.password_reset_confirm, name='password_reset_confirm'),

    url(r'^signin/$', views.signin, name='signin'),
    url(r'^signout/$', views.signout, name='signout'),
    url(r'^signup/$', views.signup, name='signup'),

    url(r'^api/statistics/charts/categories/$', statistics.categories, name='statistics_chart_categories'),
    url(r'^api/statistics/charts/tags/$', statistics.tags, name='statistics_chart_tags'),
]
