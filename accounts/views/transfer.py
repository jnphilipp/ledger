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

from accounts.forms import TransferForm
from accounts.models import Entry
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views import generic


@method_decorator(login_required, name="dispatch")
class CreateView(SuccessMessageMixin, generic.edit.FormView):
    form_class = TransferForm
    success_message = _("The entries %(entries)s were successfully created.")
    template_name = "accounts/transfer_form.html"

    def get_initial(self):
        return {"ledger": self.request.user.ledger}

    def form_valid(self, form):
        self.from_entry = Entry.objects.create(
            account=form.cleaned_data["from_account"],
            day=form.cleaned_data["from_date"],
            amount=form.cleaned_data["amount"] * -1,
            category=form.cleaned_data["to_account"].category,
        )
        self.to_entry = Entry.objects.create(
            account=form.cleaned_data["to_account"],
            day=form.cleaned_data["to_date"],
            amount=form.cleaned_data["amount"],
            category=form.cleaned_data["from_account"].category,
        )
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        entries = (
            f"{self.from_entry.account.name} - #"
            + f"{self.from_entry.serial_number}, "
            + f"{self.from_entry.account.name}"
            + f" - #{self.from_entry.serial_number}"
        )
        return self.success_message % {"entries": entries}

    def get_success_url(self):
        url = reverse_lazy("create_another_success")
        if "reload" in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        return url
