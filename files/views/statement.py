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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from files.forms import StatementFilterForm, StatementForm
from files.models import Statement


@method_decorator(login_required, name="dispatch")
class ListView(generic.ListView):
    context_object_name = "statements"
    model = Statement
    paginate_by = 200

    def get_queryset(self):
        self.form = StatementFilterForm(self.request.GET)
        self.o = "-updated_at"
        if "o" in self.request.GET:
            self.o = self.request.GET.get("o")

        statements = Statement.objects.filter(account__ledger__user=self.request.user)

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


@method_decorator(login_required, name="dispatch")
class DetailView(generic.DetailView):
    model = Statement

    def get_queryset(self):
        return Statement.objects.filter(account__ledger__user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        return FileResponse(open(self.object.file.path, "rb"), as_attachment=True)


@method_decorator(login_required, name="dispatch")
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = StatementForm
    model = Statement
    success_message = _('The statement "%(name)s" was successfully uploaded.')

    def get_initial(self):
        initial = {"uploader": self.request.user}
        if "slug" in self.kwargs:
            initial["account"] = get_object_or_404(Account, slug=self.kwargs["slug"])
        return initial

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
    form_class = StatementForm
    model = Statement
    success_message = _('The statement "%(name)s" was successfully updated.')

    def get_queryset(self):
        return Statement.objects.filter(uploader=self.request.user)

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
    model = Statement

    def get_queryset(self):
        return Statement.objects.filter(uploader=self.request.user)

    def get_success_url(self):
        msg = _('The statement "%(name)s" was successfully deleted.')
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
