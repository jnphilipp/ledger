# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Ledger Django app entry views."""

from datetime import date
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..dates import get_last_date_current_month
from ..forms import EntryForm, EntryFilterForm
from ..models import Account, Entry


class ListView(generic.ListView):
    """Entry list view."""

    context_object_name = "entries"
    model = Entry
    paginate_by = 200

    def get_queryset(self):
        """Get queryset."""
        entries = Entry.objects.order_by("-date", "account__name", "-serial_number")

        filtered = False
        self.form = None
        self.start_date = None
        self.end_date = None
        self.accounts = []
        self.categories = []
        self.tags = []
        self.units = []
        if entries.count() > 0:
            self.form = EntryFilterForm(self.request.GET)
            if self.form.is_valid():
                if self.form.cleaned_data["start_date"]:
                    filtered = True
                    self.start_date = self.form.cleaned_data["start_date"]
                    entries = entries.filter(date__gte=self.start_date)
                if self.form.cleaned_data["end_date"]:
                    filtered = True
                    self.end_date = self.form.cleaned_data["end_date"]
                    entries = entries.filter(date__lte=self.end_date)
                if (
                    "accounts" in self.form.cleaned_data
                    and self.form.cleaned_data["accounts"]
                ):
                    filtered = True
                    self.accounts = [a.pk for a in self.form.cleaned_data["accounts"]]
                    entries = entries.filter(account__in=self.accounts)
                if self.form.cleaned_data["categories"]:
                    filtered = True
                    self.categories = [
                        c.pk for c in self.form.cleaned_data["categories"]
                    ]
                    entries = entries.filter(category__in=self.categories)
                if "tags" in self.form.cleaned_data and self.form.cleaned_data["tags"]:
                    filtered = True
                    self.tags = [t.pk for t in self.form.cleaned_data["tags"]]
                    entries = entries.filter(tags__in=self.tags)
                if (
                    "units" in self.form.cleaned_data
                    and self.form.cleaned_data["units"]
                ):
                    filtered = True
                    self.units = [u.pk for u in self.form.cleaned_data["units"]]
                    entries = entries.filter(account__unit__in=self.units)

        if not filtered:
            self.end_date = get_last_date_current_month()
            if entries.count() > 0:
                self.form = EntryFilterForm(initial={"end_date": self.end_date})
            entries = entries.filter(date__lte=self.end_date)

        return entries.annotate(total=F("amount") + F("fees")).distinct()

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(*args, **kwargs)

        context["form"] = self.form
        context["start_date"] = self.start_date
        context["end_date"] = self.end_date
        context["accounts"] = self.accounts
        context["categories"] = self.categories
        context["tags"] = self.tags
        context["units"] = self.units

        return context


class DetailView(generic.DetailView):
    """Entry detail view."""

    model = Entry

    def get_object(self, queryset=None):
        """Get object."""
        if "slug" in self.kwargs and self.kwargs["slug"]:
            return Entry.objects.get(
                account__slug=self.kwargs["slug"], pk=self.kwargs["pk"]
            )
        else:
            return Entry.objects.get(pk=self.kwargs["pk"])


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """Entry create view."""

    form_class = EntryForm
    model = Entry
    success_url = reverse_lazy("create_another_success")

    def get_initial(self):
        """Get initial."""
        initial = {}
        if "slug" in self.kwargs:
            initial["account"] = get_object_or_404(Account, slug=self.kwargs["slug"])
        return initial

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The entry "%(entry)s" was successfully created.') % {
            "entry": f"{self.object.account.name} - #{self.object.serial_number}"
        }


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """Entry update view."""

    form_class = EntryForm
    model = Entry
    success_url = reverse_lazy("create_another_success")

    def form_valid(self, form):
        """Form valid."""
        self.orig_serial_number = self.object.serial_number
        return super().form_valid(form)

    def get_initial(self):
        """Get initial."""
        return {
            "show_account": "slug" not in self.kwargs,
        }

    def get_success_message(self, cleaned_data):
        """Get success message."""
        entry = "%s - #%s" % (self.object.account.name, self.orig_serial_number)
        no = "%s - #%s" % (self.object.account.name, self.object.serial_number)

        if self.orig_serial_number == self.object.serial_number:
            return _('The entry "%(entry)s" was successfully updated.') % {
                "entry": entry
            }
        else:
            return _(
                'The entry "%(entry)s" was successfully updated and'
                + ' moved to "%(no)s".'
            ) % {"entry": entry, "no": no}


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    """Entry delete view."""

    model = Entry
    success_url = reverse_lazy("create_another_success")

    def form_valid(self, form):
        """Delete."""
        v = super().form_valid(form)
        for entry in Entry.objects.filter(account=self.object.account).filter(
            serial_number__gt=self.object.serial_number
        ):
            entry.serial_number -= 1
            entry.save()
        self.object.account.save()
        return v

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The entry "%(entry)s" was successfully deleted.') % {
            "entry": f"{self.object.account.name} - #{self.object.serial_number}"
        }


class DuplicateView(generic.base.RedirectView):
    """Entry duplicate view."""

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        """Get redirect URL."""
        entry = get_object_or_404(Entry, pk=kwargs["pk"])

        new = Entry.objects.create(
            account=entry.account,
            date=date.today(),
            amount=entry.amount,
            fees=entry.fees,
            category=entry.category,
            text=entry.text,
        )
        for tag in entry.tags.all():
            new.tags.add(tag.id)
        new.save()

        msg = _(
            'The entry "%(old_entry)s" has been successfully duplicated '
            + 'as entry "%(new_entry)s".'
        )
        old_entry = f"{entry.account.name} - #{entry.serial_number}"
        new_entry = f"{new.account.name} - #{new.serial_number}"
        messages.add_message(
            self.request,
            messages.SUCCESS,
            msg % {"old_entry": old_entry, "new_entry": new_entry},
        )

        self.url = reverse_lazy("entry_list")
        return super().get_redirect_url(*args, **kwargs)


class SwapView(generic.base.RedirectView):
    """Entry swap view."""

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        """Get redirect URL."""
        e1 = get_object_or_404(Entry, id=kwargs["pk"])

        if kwargs["direction"] == "down":
            e2 = (
                Entry.objects.filter(account=e1.account)
                .filter(serial_number__lt=e1.serial_number)
                .order_by("-serial_number")[:1]
            )
        elif kwargs["direction"] == "up":
            e2 = (
                Entry.objects.filter(account=e1.account)
                .filter(serial_number__gt=e1.serial_number)
                .order_by("serial_number")[:1]
            )

        if e2.count() == 1:
            e2 = e2[0]

            tmp = e1.serial_number
            e1.serial_number = e2.serial_number
            e2.serial_number = -1
            e2.save()
            e1.save()

            e2.serial_number = tmp
            e2.save()

            msg = _(
                'The entries "#%(e1)s" and "#%(e2)s" were successfully ' + "swaped."
            )
            messages.add_message(
                self.request,
                messages.SUCCESS,
                msg % {"e1": e1.serial_number, "e2": e2.serial_number},
            )

        self.url = reverse_lazy("entry_list")
        return super().get_redirect_url(*args, **kwargs)
