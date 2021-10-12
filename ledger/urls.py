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
"""ledger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

from accounts.views.entry import ListView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import RedirectView

from .views import AnotherSuccessView, budget


# admin.site.site_header = _("ledger administration")


urlpatterns = [
    path("", ListView.as_view(), name="dashboard"),
    path("", ListView.as_view(), name="entry_list"),
    path("<int:page>/", ListView.as_view()),
    path(
        "add/another/success/",
        AnotherSuccessView.as_view(),
        name="create_another_success",
    ),
    path("budget/", budget.DetailView.as_view(), name="budget_detail"),
    path("budget/<int:year>/", budget.DetailView.as_view(), name="budget_detail"),
    path("budget/edit/", budget.UpdateView.as_view(), name="budget_edit"),
    path("accounts/", include("accounts.urls")),
    path("categories/", include("categories.urls")),
    path("files/", include("files.urls")),
    path("units/", include("units.urls")),
    # path("admin/", admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url="/static/images/logo.png")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
