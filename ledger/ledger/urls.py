# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""ledger URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic.base import RedirectView

from .views import (
    AnotherSuccessView,
    account,
    budget,
    category,
    entry,
    file,
    statistics,
    tag,
)


urlpatterns = [
    path("", entry.ListView.as_view(), name="entry_list"),
    path("<int:page>/", entry.ListView.as_view()),
    path("account/", account.ListView.as_view(), name="account_list"),
    path("account/create/", account.CreateView.as_view(), name="account_create"),
    path("account/autocomplete/", account.autocomplete, name="account_autocomplete"),
    path("account/<slug:slug>/", account.DetailView.as_view(), name="account_detail"),
    path(
        "account/<slug:slug>/edit/", account.UpdateView.as_view(), name="account_edit"
    ),
    path(
        "account/<slug:slug>/close/", account.CloseView.as_view(), name="account_close"
    ),
    path(
        "account/<slug:slug>/delete/",
        account.DeleteView.as_view(),
        name="account_delete",
    ),
    path(
        "add/another/success/",
        AnotherSuccessView.as_view(),
        name="create_another_success",
    ),
    path("budget/", budget.DetailView.as_view(), name="budget_detail"),
    path("budget/<int:year>/", budget.DetailView.as_view(), name="budget_detail"),
    path("budget/edit/", budget.UpdateView.as_view(), name="budget_edit"),
    path("category/autocomplete/", category.autocomplete, name="category_autocomplete"),
    path("entry/create/", entry.CreateView.as_view(), name="entry_create"),
    path("entry/<int:pk>/", entry.DetailView.as_view(), name="entry_detail"),
    path("entry/<int:pk>/edit/", entry.UpdateView.as_view(), name="entry_edit"),
    path("entry/<int:pk>/delete/", entry.DeleteView.as_view(), name="entry_delete"),
    path(
        "entry/<int:pk>/duplicate/",
        entry.DuplicateView.as_view(),
        name="entry_duplicate",
    ),
    path(
        "entry/<int:pk>/swap/<str:direction>/",
        entry.SwapView.as_view(),
        name="entry_swap",
    ),
    path(
        "file/create/<int:content_type>/<int:object_id>/",
        file.CreateView.as_view(),
        name="file_create",
    ),
    path("file/<slug:slug>/", file.DetailView.as_view(), name="file_detail"),
    path("file/<slug:slug>/delete/", file.DeleteView.as_view(), name="file_delete"),
    path("portfolio/", include("portfolio.urls")),
    path("statistics/", statistics.StatisticsView.as_view(), name="statistics_detail"),
    path(
        "statistics/<slug:unit>/",
        statistics.StatisticsView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/<slug:unit>/<str:chart>/",
        statistics.StatisticsView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/<slug:unit>/<str:chart>/<int:year>/",
        statistics.StatisticsView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/<slug:unit>/<str:chart>/<int:year>/<int:month>/",
        statistics.StatisticsView.as_view(),
        name="statistics_detail",
    ),
    path(
        "statistics/charts/categories/<slug:unit>/",
        statistics.categories,
        name="statistics_chart_categories",
    ),
    path(
        "statistics/charts/categories/<slug:unit>/<int:year>/",
        statistics.categories,
        name="statistics_chart_categories",
    ),
    path(
        "statistics/charts/categories/<slug:unit>/<int:year>/<int:month>/",
        statistics.categories,
        name="statistics_chart_categories",
    ),
    path(
        "statistics/charts/tags/<slug:unit>/",
        statistics.tags,
        name="statistics_chart_tags",
    ),
    path(
        "statistics/charts/tags/<slug:unit>/<int:year>/",
        statistics.tags,
        name="statistics_chart_tags",
    ),
    path(
        "statistics/charts/tags/<slug:unit>/<int:year>/<int:month>/",
        statistics.tags,
        name="statistics_chart_tags",
    ),
    path("tag/autocomplete/", tag.autocomplete, name="tag_autocomplete"),
    path("units/", include("units.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/images/logo.png")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
