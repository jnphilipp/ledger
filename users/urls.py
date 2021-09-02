# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# This file is part of ledger.
#
# ledger is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ledger is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ledger.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from .views import budget, signin, signup, statistics, UpdateView


app_name = "users"
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="profiles:profile"), name="index"),
    path("profile/", UpdateView.as_view(), name="profile"),
    path("budget/", budget.DetailView.as_view(), name="budget_detail"),
    path("budget/<int:year>/", budget.DetailView.as_view(), name="budget_detail"),
    path("budget/edit/", budget.UpdateView.as_view(), name="budget_edit"),
    path("statistics/", statistics.DetailView.as_view(), name="statistics_detail"),
    path(
        "statistics/<slug:unit>/",
        statistics.DetailView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/<slug:unit>/<str:chart>/",
        statistics.DetailView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/<slug:unit>/<str:chart>/<int:year>/",
        statistics.DetailView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/<slug:unit>/<str:chart>/<int:year>/<int:month>/",
        statistics.DetailView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/charts/categories/<slug:unit>/",
        statistics.charts.categories,
        name="statistics_chart_categories",
    ),
    path(
        "statistics/charts/categories/<slug:unit>/<int:year>/",
        statistics.charts.categories,
        name="statistics_chart_categories",
    ),
    path(
        "statistics/charts/categories/<slug:unit>/<int:year>/<int:month>/",
        statistics.charts.categories,
        name="statistics_chart_categories",
    ),
    path(
        "statistics/charts/tags/<slug:unit>/",
        statistics.charts.tags,
        name="statistics_chart_tags",
    ),
    path(
        "statistics/charts/tags/<slug:unit>/<int:year>/",
        statistics.charts.tags,
        name="statistics_chart_tags",
    ),
    path(
        "statistics/charts/tags/<slug:unit>/<int:year>/<int:month>/",
        statistics.charts.tags,
        name="statistics_chart_tags",
    ),
    path(
        "password/",
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy("users:password_change_done")
        ),
        name="password_change",
    ),
    path(
        "password/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy("users:password_reset_done")
        ),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("signin/", signin, name="signin"),
    path(
        "signout/",
        auth_views.LogoutView.as_view(template_name="registration/signout.html"),
        name="signout",
    ),
    path("signup/", signup, name="signup"),
]
