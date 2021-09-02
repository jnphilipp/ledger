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

from .views import autocomplete, ListView, CreateView, DetailView, UpdateView


app_name = "units"
urlpatterns = [
    path("", ListView.as_view(), name="list"),
    path("add/", CreateView.as_view(), name="create"),
    path("add/another/", CreateView.as_view(), name="create_another"),
    path("autocomplete/", autocomplete, name="unit_autocomplete"),
    path("<slug:slug>/", DetailView.as_view(), name="detail"),
    path("<slug:slug>/edit/", UpdateView.as_view(), name="edit"),
]
