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

from django.urls import path

from .views import category, tag


app_name = "categories"
urlpatterns = [
    path("category/", category.ListView.as_view(), name="category_list"),
    path("category/autocomplete/", category.autocomplete, name="category_autocomplete"),
    path(
        "category/<slug:slug>/", category.DetailView.as_view(), name="category_detail"
    ),
    path(
        "category/<slug:slug>/<int:year>/",
        category.DetailView.as_view(),
        name="category_detail",
    ),
    path(
        "category/<slug:slug>/charts/statistics/",
        category.charts.statistics,
        name="category_chart_statistics",
    ),
    path(
        "category/<slug:slug>/charts/statistics/<int:year>/",
        category.charts.statistics,
        name="category_chart_statistics",
    ),
    path(
        "category/<slug:slug>/delete/",
        category.DeleteView.as_view(),
        name="category_delete",
    ),
    path(
        "category/<slug:slug>/edit/",
        category.UpdateView.as_view(),
        name="category_edit",
    ),
    path("tag/", tag.ListView.as_view(), name="tag_list"),
    path("tag/autocomplete/", tag.autocomplete, name="tag_autocomplete"),
    path("tag/<slug:slug>/", tag.DetailView.as_view(), name="tag_detail"),
    path("tag/<slug:slug>/<int:year>/", tag.DetailView.as_view(), name="tag_detail"),
    path(
        "tag/<slug:slug>/charts/statistics/",
        tag.charts.statistics,
        name="tag_chart_statistics",
    ),
    path(
        "tag/<slug:slug>/charts/statistics/<int:year>/",
        tag.charts.statistics,
        name="tag_chart_statistics",
    ),
    path("tag/<slug:slug>/edit/", tag.UpdateView.as_view(), name="tag_edit"),
    path("tag/<slug:slug>/delete/", tag.DeleteView.as_view(), name="tag_delete"),
]
