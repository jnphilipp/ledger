# -*- coding: utf-8 -*-

from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView

from .views import budget, signin, signup, statistics, UpdateView


app_name = 'users'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='profiles:profile'),
         name='index'),
    path('profile/', UpdateView.as_view(), name='profile'),

    path('budget/', budget.budget, name='budget'),
    path('budget/edit/', budget.edit, name='budget_edit'),
    path('statistics/', statistics.detail, name='statistics'),
    path('statistics/charts/categories/', statistics.charts.categories,
         name='statistics_chart_categories'),
    path('statistics/charts/tags/', statistics.charts.tags,
         name='statistics_chart_tags'),

    path('password/', auth_views.PasswordChangeView.as_view(
         success_url='/profiles/password/done/'), name='password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),


    path('password/reset/', auth_views.PasswordResetView.as_view(
         success_url='/profiles/password/reset/done/'), name='password_reset'),

    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),

    path('password/reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    path('password/reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('signin/', signin, name='signin'),
    path('signout/', auth_views.LogoutView.as_view(
         template_name='registration/signout.html'), name='signout'),
    path('signup/', signup, name='signup'),
]
