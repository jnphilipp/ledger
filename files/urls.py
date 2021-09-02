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

from .views import invoice, statement


app_name = "files"
urlpatterns = [
    path("invoice/<slug:slug>", invoice.DetailView.as_view(), name="invoice_detail"),
    path(
        "invoice/<int:entry>/create/",
        invoice.CreateView.as_view(),
        name="invoice_create",
    ),
    path(
        "invoice/<slug:slug>/delete/",
        invoice.DeleteView.as_view(),
        name="invoice_delete",
    ),
    path(
        "invoice/<slug:slug>/edit/", invoice.UpdateView.as_view(), name="invoice_edit"
    ),
    path("statement/", statement.ListView.as_view(), name="statement_list"),
    path("statement/create/", statement.CreateView.as_view(), name="statement_create"),
    path(
        "statement/create/<slug:slug>",
        statement.CreateView.as_view(),
        name="statement_create",
    ),
    path(
        "statement/<slug:slug>", statement.DetailView.as_view(), name="statement_detail"
    ),
    path(
        "statement/<slug:slug>/delete/",
        statement.DeleteView.as_view(),
        name="statement_delete",
    ),
    path(
        "statement/<slug:slug>/edit/",
        statement.UpdateView.as_view(),
        name="statement_edit",
    ),
]
