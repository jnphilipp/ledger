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

from accounts.models import Entry
from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from files.forms import InvoiceForm
from files.models import Invoice


class DetailView(generic.DetailView):
    model = Invoice

    def render_to_response(self, context, **response_kwargs):
        return FileResponse(open(self.object.file.path, "rb"), as_attachment=True)


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = InvoiceForm
    model = Invoice
    success_message = _('The invoice "%(name)s" was successfully uploaded.')
    success_url = reverse_lazy("create_another_success")

    def get_initial(self):
        return {
            "entry": get_object_or_404(Entry, pk=self.kwargs["entry"])
        }

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object.name}


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = InvoiceForm
    model = Invoice
    success_message = _('The invoice "%(name)s" was successfully updated.')
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object.name}


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    model = Invoice
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        return _('The invoice "%(name)s" was successfully deleted.') % {"name": self.object.name}
