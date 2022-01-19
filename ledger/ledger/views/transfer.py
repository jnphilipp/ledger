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
"""Ledger Django app transfer views."""

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..forms import TransferForm
from ..models import Entry


class CreateView(SuccessMessageMixin, generic.edit.FormView):
    """Transfer create view."""

    form_class = TransferForm
    success_message = _("The entries %(entries)s were successfully created.")
    success_url = reverse_lazy("create_another_success")
    template_name = "ledger/transfer_form.html"

    def form_valid(self, form):
        """Form valid."""
        self.from_entry = Entry.objects.create(
            account=form.cleaned_data["from_account"],
            date=form.cleaned_data["from_date"],
            amount=form.cleaned_data["amount"] * -1,
            fees=form.cleaned_data["fees"],
            category=form.cleaned_data["to_account"].category,
        )
        self.to_entry = Entry.objects.create(
            account=form.cleaned_data["to_account"],
            date=form.cleaned_data["to_date"],
            amount=form.cleaned_data["amount"],
            category=form.cleaned_data["from_account"].category,
        )
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {
            "entries": f"{self.from_entry.account.name} - #"
            + f"{self.from_entry.serial_number}, "
            + f"{self.to_entry.account.name}"
            + f" - #{self.to_entry.serial_number}"
        }