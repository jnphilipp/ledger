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

from accounts.forms import AccountForm
from accounts.models import Account
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic


class ListView(generic.ListView):
    context_object_name = "accounts"
    model = Account
    ordering = ["unit__name", "closed", "name"]


class DetailView(generic.DetailView):
    model = Account

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)

        if "categories_year" not in self.kwargs:
            years = context["account"].entries.dates("date", "year")
            context["categories_years"] = [y.strftime("%Y") for y in years]
        else:
            context["categories_year"] = self.kwargs["categories_year"]

        if "categories_month" not in self.kwargs and "categories_year" in self.kwargs:
            months = (
                context["account"]
                .entries.filter(date__year=context["categories_year"])
                .dates("date", "month")
            )
            context["categories_months"] = [
                (m.strftime("%m"), m.strftime("%B")) for m in months
            ]
        elif "categories_month" in self.kwargs:
            context["categories_month"] = self.kwargs["categories_month"]

        if "tags_year" not in self.kwargs:
            years = (
                context["account"]
                .entries.filter(tags__isnull=False)
                .dates("date", "year")
            )
            context["tags_years"] = [y.strftime("%Y") for y in years]
        else:
            context["tags_year"] = self.kwargs["tags_year"]

        if "tags_month" not in self.kwargs and "tags_year" in self.kwargs:
            months = (
                context["account"]
                .entries.filter(tags__isnull=False)
                .filter(date__year=context["tags_year"])
                .dates("date", "month")
            )
            context["tags_months"] = [
                (m.strftime("%m"), m.strftime("%B")) for m in months
            ]
        elif "tags_month" in self.kwargs:
            context["tags_month"] = self.kwargs["tags_month"]

        return context


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = AccountForm
    model = Account
    success_message = _('The account "%(name)s" was successfully created.')

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object.name}

    def get_success_url(self):
        if "next" in self.request.GET:
            redirect = self.request.GET.get("next")
        else:
            redirect = reverse_lazy("accounts:account_detail", args=[self.object.slug])

        return f'{reverse_lazy("create_another_success")}?next={redirect}'


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = AccountForm
    model = Account
    success_message = _('The account "%(name)s" was successfully updated.')

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object.name}

    def get_success_url(self):
        if "next" in self.request.GET:
            redirect = self.request.GET.get("next")
        else:
            redirect = reverse_lazy("accounts:account_detail", args=[self.object.slug])

        return f'{reverse_lazy("create_another_success")}?next={redirect}'


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    model = Account
    success_message = _('The account "%(name)s" was successfully deleted.')

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object.name}

    def get_success_url(self):
        return f"{reverse_lazy('create_another_success')}?next=" + \
            f"{reverse_lazy('accounts:account_list')}"


class CloseView(generic.base.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        account = get_object_or_404(Account, slug=kwargs["slug"])
        account.closed = not account.closed
        account.save()

        if account.closed:
            msg = _("The account %(name)s was successfully closed.")
        else:
            msg = _("The account %(name)s was successfully re-open.")

        msg %= {"name": account.name}
        messages.add_message(self.request, messages.SUCCESS, msg)
        return reverse_lazy("accounts:account_list")
