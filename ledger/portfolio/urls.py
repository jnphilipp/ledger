# Copyright (C) 2014-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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

from .views import closing, position, trade, tradeable


app_name = "portfolio"
urlpatterns = [
    path("", position.ListView.as_view(), name="position_list"),
    path("<int:page>/", position.ListView.as_view()),
    path("closing/create/", closing.CreateView.as_view(), name="closing_create"),
    path("position/autocomplete/", position.autocomplete, name="position_autocomplete"),
    path("position/create/", position.CreateView.as_view(), name="position_create"),
    path(
        "position/<slug:slug>/", position.DetailView.as_view(), name="position_detail"
    ),
    path("position/<slug:slug>/chart/", position.chart, name="position_chart"),
    path(
        "position/<slug:slug>/close/",
        position.CloseView.as_view(),
        name="position_close",
    ),
    path(
        "position/<slug:slug>/delete/",
        position.DeleteView.as_view(),
        name="position_delete",
    ),
    path(
        "position/<slug:slug>/edit/",
        position.UpdateView.as_view(),
        name="position_edit",
    ),
    path("trade/create/", trade.CreateView.as_view(), name="trade_create"),
    path("trade/<int:pk>/delete/", trade.DeleteView.as_view(), name="trade_delete"),
    path("trade/<int:pk>/edit/", trade.UpdateView.as_view(), name="trade_edit"),
    path(
        "tradeable/autocomplete/", tradeable.autocomplete, name="tradeable_autocomplete"
    ),
    path("tradeable/create/", tradeable.CreateView.as_view(), name="tradeable_create"),
    path(
        "tradeable/<slug:slug>/edit/",
        tradeable.UpdateView.as_view(),
        name="tradeable_edit",
    ),
]
