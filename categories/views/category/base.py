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

from categories.forms import CategoryForm
from categories.models import Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Func, Q
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic


class ListView(generic.ListView):
    context_object_name = "categories"
    model = Category

    def get_queryset(self):
        return (
            Category.objects
            .annotate(lname=Func(F("name"), function="LOWER"))
            .order_by("lname")
        )


class DetailView(generic.DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context["entry_list"] = context["category"].entries.all()

        if "year" not in self.kwargs:
            years = (
                context["category"]
                .entries.dates("date", "year")
            )
            context["years"] = [y.strftime("%Y") for y in years]
        else:
            context["year"] = self.kwargs["year"]

        return context


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = CategoryForm
    model = Category
    success_message = _('The category "%(name)s" was successfully updated.')

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object.name}

    def get_success_url(self):
        url = reverse_lazy("create_another_success")
        if "reload" in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}&next={reverse_lazy("categories:category_detail", args=[self.object.slug])}'
        elif "target_id" in self.request.GET:
            url = (
                f'{url}?target_id={self.request.GET.get("target_id")}&'
                + f"value={self.object.pk}&name={self.object.name}"
            )
        return url


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    model = Category
    success_message = _('The category "%(name)s" was successfully deleted.')

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object.name}

    def get_success_url(self):
        url = reverse_lazy("create_another_success")
        if "reload" in self.request.GET:
            url = (
                f'{url}?reload={self.request.GET.get("reload")}&next='
                + f'{reverse_lazy("categories:category_list")}'
            )
        elif "target_id" in self.request.GET:
            url = (
                f'{url}?target_id={self.request.GET.get("target_id")}&'
                + f"value={self.object.pk}&name={self.object.name}"
            )
        return url
