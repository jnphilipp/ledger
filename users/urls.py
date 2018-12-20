# -*- coding: utf-8 -*-

from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from .views import budget, signin, signup, statistics, UpdateView


app_name = 'users'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='profiles:profile'),
         name='index'),
    path('profile/', UpdateView.as_view(), name='profile'),

    path('budget/', budget.DetailView.as_view(), name='budget_detail'),
    path('budget/<int:year>/', budget.DetailView.as_view(),
         name='budget_detail'),
    path('budget/edit/', budget.UpdateView.as_view(), name='budget_edit'),

    path('statistics/', statistics.DetailView.as_view(),
         name='statistics_detail'),
    path('statistics/<slug:unit>/', statistics.DetailView.as_view(),
         name='statistics_detail'),
    path('statistics/<slug:unit>/<str:chart>/', statistics.DetailView.as_view(),
         name='statistics_detail'),
    path('statistics/<slug:unit>/<str:chart>/<int:year>/',
         statistics.DetailView.as_view(), name='statistics_detail'),
    path('statistics/<slug:unit>/<str:chart>/<int:year>/<int:month>/',
         statistics.DetailView.as_view(), name='statistics_detail'),
    path('statistics/charts/categories/<slug:unit>/',
         statistics.charts.categories, name='statistics_chart_categories'),
    path('statistics/charts/categories/<slug:unit>/<int:year>/',
         statistics.charts.categories, name='statistics_chart_categories'),
    path('statistics/charts/categories/<slug:unit>/<int:year>/<int:month>/',
         statistics.charts.categories, name='statistics_chart_categories'),
    path('statistics/charts/tags/<slug:unit>/',
         statistics.charts.tags, name='statistics_chart_tags'),
    path('statistics/charts/tags/<slug:unit>/<int:year>/',
         statistics.charts.tags, name='statistics_chart_tags'),
    path('statistics/charts/tags/<slug:unit>/<int:year>/<int:month>/',
         statistics.charts.tags, name='statistics_chart_tags'),

    path('password/', auth_views.PasswordChangeView.as_view(
         success_url=reverse_lazy('users:password_change_done')),
         name='password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('password/reset/', auth_views.PasswordResetView.as_view(
         success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset'),

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
