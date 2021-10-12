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
"""Portfolio Django app position views."""

# from accounts.forms import EntryForm, EntryFilterForm
# from accounts.models import Account, Entry
# from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import floatformat
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
# from ledger.dates import get_last_date_current_month
from typing import Any, Dict
from users.models import Portfolio

from ..forms import PositionForm
from ..models import Position


@method_decorator(login_required, name="dispatch")
class ListView(generic.ListView):
    context_object_name = "positions"
    model = Position
    paginate_by = 200

    def get_queryset(self):
        # self.form = EntryFilterForm(self.request.GET)

        positions = Position.objects.all().order_by("closed")

        # filtered = False
        # self.start_date = None
        # self.end_date = None
        # self.accounts = []
        # self.categories = []
        # self.tags = []
        # self.units = []
        # if self.form.is_valid():
        #     if self.form.cleaned_data["start_date"]:
        #         filtered = True
        #         self.start_date = self.form.cleaned_data["start_date"]
        #         entries = entries.filter(day__gte=self.start_date)
        #     if self.form.cleaned_data["end_date"]:
        #         filtered = True
        #         self.end_date = self.form.cleaned_data["end_date"]
        #         entries = entries.filter(day__lte=self.end_date)
        #     if (
        #         "accounts" in self.form.cleaned_data
        #         and self.form.cleaned_data["accounts"]
        #     ):
        #         filtered = True
        #         self.accounts = [a.pk for a in self.form.cleaned_data["accounts"]]
        #         entries = entries.filter(account__in=self.accounts)
        #     if self.form.cleaned_data["categories"]:
        #         filtered = True
        #         self.categories = [c.pk for c in self.form.cleaned_data["categories"]]
        #         entries = entries.filter(category__in=self.categories)
        #     if self.form.cleaned_data["tags"]:
        #         filtered = True
        #         self.tags = [t.pk for t in self.form.cleaned_data["tags"]]
        #         entries = entries.filter(tags__in=self.tags)
        #     if "units" in self.form.cleaned_data and self.form.cleaned_data["units"]:
        #         filtered = True
        #         self.units = [u.pk for u in self.form.cleaned_data["units"]]
        #         entries = entries.filter(account__unit__in=self.units)

        # if not filtered:
        #     self.end_date = get_last_date_current_month()
        #     self.form = EntryFilterForm(initial={"end_date": self.end_date})
        #     entries = entries.filter(day__lte=self.end_date)

        #     if "slug" in self.kwargs:
        #         del self.form.fields["accounts"]
        #         del self.form.fields["units"]

        # entries = entries.annotate(total=F("amount") + F("fees"))
        return positions.distinct()

    def get_context_data(self, *args, **kwargs):
        context = super(ListView, self).get_context_data(*args, **kwargs)

        # context["form"] = self.form
        # context["start_date"] = self.start_date
        # context["end_date"] = self.end_date
        # context["accounts"] = self.accounts
        # context["categories"] = self.categories
        # context["tags"] = self.tags
        # context["units"] = self.units
        # if "slug" in self.kwargs:
        #     context["account"] = self.account
        #     context["show_options"] = not context["account"].closed
        # else:
        #     context["show_options"] = True

        return context


@method_decorator(login_required, name="dispatch")
class DetailView(generic.DetailView):
    model = Position


@method_decorator(login_required, name="dispatch")
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = PositionForm
    model = Position
    success_message = _('The position for "%(position)s" was successfully created.')

    def get_initial(self) -> Dict[str, Any]:
        return {"portfolio": self.request.user.portfolio}

    def get_success_message(self, cleaned_data):
        return self.success_message % {"position": self.object.content_object.name}

    def get_success_url(self):
        url = reverse_lazy("create_another_success")
        if "reload" in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        elif "target_id" in self.request.GET:
            url = (
                f'{url}?target_id={self.request.GET.get("target_id")}&'
                + f"value={self.object.pk}&name={self.object.name}"
            )
        return url
