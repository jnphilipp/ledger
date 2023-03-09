# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2023 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Ledger Django app account views."""

import json

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..forms import AccountForm
from ..models import Account


def autocomplete(request):
    """Handels GET/POST request to autocomplete accounts.

    GET/POST parameters:
    q --- search term
    """

    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    accounts = Account.objects.annotate(Count("entries")).order_by("-entries__count")
    if "q" in params:
        q = params.pop("q")[0]
        accounts = accounts.filter(name__icontains=q)
    if "closed" in params:
        closed = True if params.pop("closed")[0].lower() == "true" else False
        accounts = accounts.filter(closed=closed)

    data = {
        "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
        "accounts": [{"id": account.id, "text": account.name} for account in accounts],
    }
    return JsonResponse(data)


class ListView(generic.ListView):
    """Account list view."""

    context_object_name = "accounts"
    model = Account
    ordering = ["unit__name", "closed", "name"]


class DetailView(generic.DetailView):
    """Account detail view."""

    model = Account


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """Account create view."""

    form_class = AccountForm
    model = Account
    success_message = _('The account "%(name)s" was successfully created.')
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {"name": self.object.name}


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """Account update view."""

    form_class = AccountForm
    model = Account

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The account "%(name)s" was successfully updated.') % {
            "name": self.object.name
        }

    def get_success_url(self):
        """Get success URL."""
        if "next" in self.request.GET:
            redirect = self.request.GET.get("next")
        else:
            redirect = reverse_lazy("account_detail", args=[self.object.slug])

        return f'{reverse_lazy("create_another_success")}?next={redirect}'


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    """Account delete view."""

    model = Account

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The account "%(name)s" was successfully deleted.') % {
            "name": self.object.name
        }

    def get_success_url(self):
        """Get success URL."""
        return (
            f"{reverse_lazy('create_another_success')}?next="
            + f"{reverse_lazy('account_list')}"
        )


class CloseView(generic.base.RedirectView):
    """Account close view."""

    def get_redirect_url(self, *args, **kwargs):
        """Get redirect URL."""
        account = get_object_or_404(Account, slug=kwargs["slug"])
        account.closed = not account.closed
        account.save()

        if account.closed:
            msg = _("The account %(name)s was successfully closed.")
        else:
            msg = _("The account %(name)s was successfully re-open.")

        msg %= {"name": account.name}
        messages.add_message(self.request, messages.SUCCESS, msg)
        return reverse_lazy("account_list")
