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

from accounts.models import Account
from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from files.forms import StatementFilterForm, StatementForm
from files.models import Statement


class ListView(generic.ListView):
    context_object_name = "statements"
    model = Statement
    paginate_by = 200

    def get_queryset(self):
        self.form = StatementFilterForm(self.request.GET)
        self.o = "-updated_at"
        if "o" in self.request.GET:
            self.o = self.request.GET.get("o")

        statements = Statement.objects.all()

        self.accounts = []
        if self.form.is_valid():
            if (
                "accounts" in self.form.cleaned_data
                and self.form.cleaned_data["accounts"]
            ):
                self.accounts = [a.pk for a in self.form.cleaned_data["accounts"]]
                statements = statements.filter(account__in=self.accounts)

        return statements.order_by(self.o)

    def get_context_data(self, *args, **kwargs):
        context = super(ListView, self).get_context_data(*args, **kwargs)
        context["form"] = self.form
        context["accounts"] = self.accounts
        context["o"] = self.o
        return context


class DetailView(generic.DetailView):
    model = Statement

    def render_to_response(self, context, **response_kwargs):
        return FileResponse(open(self.object.file.path, "rb"), as_attachment=True)


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = StatementForm
    model = Statement
    success_url = reverse_lazy("create_another_success")

    def get_initial(self):
        initial = {}
        if "slug" in self.kwargs:
            initial["account"] = get_object_or_404(Account, slug=self.kwargs["slug"])
        return initial

    def get_success_message(self, cleaned_data):
        return _('The statement "%(name)s" was successfully uploaded.') % {
            "name": self.object.name
        }


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = StatementForm
    model = Statement
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        return _('The statement "%(name)s" was successfully updated.') % {
            "name": self.object.name
        }


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    model = Statement
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        return _('The statement "%(name)s" was successfully deleted.') % {
            "name": self.object.name
        }
