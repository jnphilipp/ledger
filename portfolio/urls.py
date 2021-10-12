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
"""Portfolio Django app urls."""

from django.urls import path

from .views import fund, position, stock


app_name = "portfolio"
urlpatterns = [
    path("", position.ListView.as_view(), name="position_list"),
    path("<int:page>/", position.ListView.as_view()),
    path("position/create/", position.CreateView.as_view(), name="position_create"),
    path("position/<slug:slug>/", position.DetailView.as_view(), name="position_detail"),

    path("tradeable/fund/autocomplete/", fund.autocomplete, name="fund_autocomplete"),
    path("tradeable/stock/autocomplete/", stock.autocomplete, name="stock_autocomplete"),
]
