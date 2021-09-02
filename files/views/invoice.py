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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from files.forms import InvoiceForm
from files.models import Invoice


@method_decorator(login_required, name="dispatch")
class DetailView(generic.DetailView):
    model = Invoice

    def get_queryset(self):
        return Invoice.objects.filter(entry__account__ledger__user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        return FileResponse(open(self.object.file.path, "rb"), as_attachment=True)


@method_decorator(login_required, name="dispatch")
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = InvoiceForm
    model = Invoice
    success_message = _('The invoice "%(name)s" was successfully uploaded.')

    def get_initial(self):
        entry = get_object_or_404(Entry, pk=self.kwargs["entry"])
        return {"uploader": self.request.user, "entry": entry}

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


@method_decorator(login_required, name="dispatch")
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = InvoiceForm
    model = Invoice
    success_message = _('The invoice "%(name)s" was successfully updated.')

    def get_queryset(self):
        return Invoice.objects.filter(uploader=self.request.user)

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


@method_decorator(login_required, name="dispatch")
class DeleteView(generic.edit.DeleteView):
    model = Invoice

    def get_queryset(self):
        return Invoice.objects.filter(uploader=self.request.user)

    def get_success_url(self):
        msg = _('The invoice "%(name)s" was successfully deleted.')
        msg %= {"name": self.object.name}
        messages.add_message(self.request, messages.SUCCESS, msg)

        url = reverse_lazy("create_another_success")
        if "reload" in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        elif "target_id" in self.request.GET:
            url = (
                f'{url}?target_id={self.request.GET.get("target_id")}&'
                + f"value={self.object.pk}&name={self.object.name}"
            )
        return url
