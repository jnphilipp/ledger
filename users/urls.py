# -*- coding: utf-8 -*-

from django.urls import path

from . import views
from .views import budget
from .views.api import statistics


app_name = 'users'
urlpatterns = [
    path('', views.profile, name='users'),
    path('profile/', views.profile, name='profile'),

    path('budget/', budget.budget, name='budget'),
    path('budget/edit/', budget.edit, name='budget_edit'),
    path('statistics/', views.statistics, name='statistics'),

    path('password/', views.password_change, name='password_change'),
    path('password/done/', views.password_change_done,
         name='password_change_done'),
    path('password/reset/', views.password_reset, name='password_reset'),
    path('password/reset/done/', views.password_reset_done,
         name='password_reset_done'),
    path('password/reset/complete/', views.password_reset_complete,
         name='password_reset_complete'),
    path('password/reset/confirm/<uidb64>/<token>/',
         views.password_reset_confirm, name='password_reset_confirm'),

    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),

    path('api/statistics/charts/categories/', statistics.categories,
         name='statistics_chart_categories'),
    path('api/statistics/charts/tags/', statistics.tags,
         name='statistics_chart_tags'),
]
