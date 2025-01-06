# Copyright (C) 2014-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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

import csv
import io
import json

from datetime import date
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, TextField, Value
from django.db.models.functions import Concat
from django.http import HttpRequest, HttpResponse, FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic
from typing import Iterable
from units.templatetags.units import unitformat

from ..dates import get_last_date_current_month
from ..forms import EntryForm, EntryFilterForm
from ..models import Account, Entry


def autocomplete(request):
    """Handels GET/POST request to autocomplete entries.

    GET/POST parameters:
    q --- search term
    """
    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    entries = Entry.objects.annotate(
        name=Concat(
            "account__name", Value(" #"), "serial_number", output_field=TextField()
        )
    ).order_by("account__name", "-serial_number")
    q = None
    if "q" in params:
        q = params.pop("q")[0]
        entries = entries.filter(name__icontains=q)

    data = {
        "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
        "entries": [{"id": tag.id, "text": tag.name} for tag in entries],
    }
    return JsonResponse(data)


class ListView(generic.ListView):
    """Entry list view."""

    context_object_name = "entries"
    model = Entry

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle GET request."""
        if "/download/" in self.request.path:
            queryset = self.get_queryset()
            buffer = io.StringIO()
            writer = csv.DictWriter(
                buffer,
                fieldnames=[
                    "account",
                    "serial_number",
                    "date",
                    "amount",
                    "category",
                    "text",
                    "tags",
                ],
                dialect="unix",
            )
            writer.writeheader()
            for entry in queryset:
                writer.writerow(
                    {
                        "account": entry.account.name,
                        "serial_number": entry.serial_number,
                        "date": entry.date.strftime("%Y-%m-%d"),
                        "amount": unitformat(entry.total, entry.account.unit),
                        "category": entry.category.name,
                        "text": entry.text,
                        "tags": ",".join(tag.name for tag in entry.tags.all()),
                    }
                )

            content = buffer.getvalue().encode("utf-8")
            bytes_io = io.BytesIO(content)
            buffer.close()

            bytes_io.seek(0)
            return FileResponse(bytes_io, as_attachment=False, filename="ledger.csv")
        else:
            return super().get(request, *args, **kwargs)

    def get_paginate_by(self, queryset) -> int | None:
        """Get number to paginate by."""
        self.per_page: int | None = None
        try:
            self.per_page = int(self.request.GET.get("per_page", 300))
            if self.per_page <= 0:
                self.per_page = None
                return self.per_page
            return self.per_page
        except ValueError:
            return self.per_page

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
        context["per_page"] = self.per_page

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

    def get_initial(self):
        """Get initial."""
        initial = {}
        if "slug" in self.kwargs:
            initial["account"] = get_object_or_404(Account, slug=self.kwargs["slug"])
        return initial

    def get_success_message(self, cleaned_data):
        """Get success message."""
        if isinstance(self.object, Iterable):
            return _("The entries %(entries)s were successfully created.") % {
                "entries": f'{", ".join(str(e) for e in self.object)}'
            }
        else:
            return _('The entry "%(entry)s" was successfully created.') % {
                "entry": self.object
            }

    def get_success_url(self):
        """Get success URL."""
        return reverse_lazy("create_another_success")


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """Entry update view."""

    form_class = EntryForm
    model = Entry
    success_url = reverse_lazy("create_another_success")

    def form_valid(self, form):
        """Form valid."""
        self.orig_sno = self.object.serial_number

        self.orig_rel = None
        self.orig_rel_sno = None
        if self.object.related is not None:
            self.orig_rel = self.object.related
            self.orig_rel_sno = self.object.related.serial_number

        return super().form_valid(form)

    def get_initial(self):
        """Get initial."""
        return {
            "show_account": "slug" not in self.kwargs,
        }

    def get_success_message(self, cleaned_data):
        """Get success message."""
        entry = f"{self.object.account.name} #{self.orig_sno}"
        no = f"{self.object.account.name} #{self.object.serial_number}"

        if self.object.related is not None and self.object.related != self.orig_rel:
            self.orig_rel.related = None
            self.orig_rel.save()
            self.object.related.related = self.object
            self.object.related.save()

            entry2 = (
                f"{self.object.related.account.name} "
                + f"#{self.object.related.serial_number}"
            )

            orig_entry = f"{self.orig_rel.account.name} #{self.orig_rel_sno}"
            orig_no = f"{self.orig_rel.account.name} #{self.orig_rel.serial_number}"

            if (
                self.orig_sno == self.object.serial_number
                and self.orig_rel.serial_number == self.orig_rel_sno
            ):
                return _(
                    'The entry "%(entry)s" was successfully updated and has a new '
                    + 'relation to "%(entry2)s".'
                ) % {
                    "entry": entry,
                    "entry2": entry2,
                }
            elif (
                self.orig_sno == self.object.serial_number
                and self.orig_rel.serial_number != self.orig_rel_sno
            ):
                return _(
                    'The entry "%(entry)s" was successfully updated and has a new '
                    + 'relation to "%(entry2)s". The original related entry '
                    + '"%(orig_entry)s" was moved to "%(orig_no)s".'
                ) % {
                    "entry": entry,
                    "entry2": entry2,
                    "orig_entry": orig_entry,
                    "orig_no": orig_no,
                }
            elif (
                self.orig_sno != self.object.serial_number
                and self.orig_rel.serial_number == self.orig_rel_sno
            ):
                return _(
                    'The entry "%(entry)s" was successfully updated and moved to '
                    + '"%(no)s and has a new relation to "%(entry2)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                    "entry2": entry2,
                }
            else:
                return _(
                    'The entry "%(entry)s" was successfully updated and moved to '
                    + '"%(no)s and has a new relation to "%(entry2)s". The original '
                    + 'related entry "%(orig_entry)s" was moved to "%(orig_no)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                    "entry2": entry2,
                    "orig_entry": orig_entry,
                    "orig_no": orig_no,
                }
        elif self.object.related is not None and self.object.related == self.orig_rel:
            entry2 = f"{self.object.related.account.name} #{self.orig_sno}"
            no2 = (
                f"{self.object.related.account.name} "
                + f"#{self.object.related.serial_number}"
            )

            if (
                self.orig_sno == self.object.serial_number
                and self.orig_rel.serial_number == self.orig_rel_sno
            ):
                return _(
                    'The entries "%(entry)s" and "%(entry2)s" were successfully '
                    + "updated."
                ) % {
                    "entry": entry,
                    "entry2": entry2,
                }
            elif (
                self.orig_sno != self.object.serial_number
                and self.orig_rel.serial_number == self.orig_rel_sno
            ):
                return _(
                    'The entries "%(entry)s" and "%(entry2)s" were successfully '
                    + 'updated and the entry "%(entry)s" was moved to "%(no)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                    "entry2": entry2,
                }
            elif (
                self.orig_sno != self.object.serial_number
                and self.orig_rel.serial_number != self.orig_rel_sno
            ):
                return _(
                    'The entries "%(entry)s" and "%(entry2)s" were successfully '
                    + 'updated and moved to "%(no)s" and "%(no2)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                    "entry2": entry2,
                    "no2": no2,
                }
            elif (
                self.orig_sno == self.object.serial_number
                and self.orig_rel.serial_number != self.orig_rel_sno
            ):
                return _(
                    'The entries "%(entry)s" and "%(entry2)s" were successfully '
                    + 'updated and the entry "%(entry2)s" was moved to "%(no2)s".'
                ) % {
                    "entry": entry,
                    "entry2": entry2,
                    "no2": no2,
                }
        elif self.object.related is not None and self.orig_rel is None:
            entry2 = (
                f"{self.object.related.account.name} "
                + f"#{self.object.related.serial_number}"
            )

            if self.orig_sno == self.object.serial_number:
                return _(
                    'The entry "%(entry)s" was successfully updated and has a new '
                    + 'relation to "%(entry2)s".'
                ) % {
                    "entry": entry,
                    "entry2": entry2,
                }
            else:
                return _(
                    'The entry "%(entry)s" was successfully updated and moved to '
                    + '"%(no)s" and has a new relation to "%(entry2)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                    "entry2": entry2,
                }
        elif self.object.related is None and self.orig_rel is not None:
            self.orig_rel.related = None
            self.orig_rel.save()

            orig_entry = f"{self.orig_rel.account.name} #{self.orig_rel_sno}"
            orig_no = f"{self.orig_rel.account.name} #{self.orig_rel.serial_number}"

            if (
                self.orig_sno == self.object.serial_number
                and self.orig_rel.serial_number == self.orig_rel_sno
            ):
                return _(
                    'The entry "%(entry)s" was successfully updated and is no longer '
                    + 'related to "%(orig_entry)s".'
                ) % {
                    "entry": entry,
                    "entry2": entry2,
                }
            elif (
                self.orig_sno == self.object.serial_number
                and self.orig_rel.serial_number != self.orig_rel_sno
            ):
                return _(
                    'The entry "%(entry)s" was successfully updated and is no longer '
                    + 'related to "%(orig_entry)s", which was moved to "%(orig_no)s".'
                ) % {
                    "entry": entry,
                    "orig_entry": orig_entry,
                    "orig_no": orig_no,
                }
            elif (
                self.orig_sno != self.object.serial_number
                and self.orig_rel.serial_number == self.orig_rel_sno
            ):
                return _(
                    'The entry "%(entry)s" was successfully updated and moved to '
                    + '"%(no)s" and is no longer related to "%(orig_entry)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                    "orig_entry": orig_entry,
                }
            elif (
                self.orig_sno != self.object.serial_number
                and self.orig_rel.serial_number != self.orig_rel_sno
            ):
                return _(
                    'The entry "%(entry)s" was successfully updated and moved to '
                    + '"%(no)s" and is no longer related to "%(orig_entry)s", which '
                    + 'was moved to "%(orig_no)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                    "orig_entry": orig_entry,
                    "orig_no": orig_no,
                }
        else:
            if self.orig_sno == self.object.serial_number:
                return _('The entry "%(entry)s" was successfully updated.') % {
                    "entry": entry
                }
            else:
                return _(
                    'The entry "%(entry)s" was successfully updated and moved to '
                    + '"%(no)s".'
                ) % {
                    "entry": entry,
                    "no": no,
                }


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
        if self.object.related is not None:
            return _(
                'The entries "%(entry1)s" and "%(entry2)s" were successfully deleted.'
            ) % {
                "entry1": f"{self.object.account.name} #{self.object.serial_number}",
                "entry2": f"{self.object.related.account.name} "
                + f"#{self.object.related.serial_number}",
            }
        else:
            return _('The entry "%(entry)s" was successfully deleted.') % {
                "entry": f"{self.object.account.name} #{self.object.serial_number}"
            }


class DuplicateView(CreateView):
    """Entry duplicate view."""

    def get_initial(self):
        """Get initial."""
        entry = get_object_or_404(Entry, pk=self.kwargs["pk"])
        return {
            "account": entry.account,
            "date": date.today(),
            "amount": entry.amount,
            "fees": entry.fees,
            "category": entry.category,
            "text": entry.text,
            "tags": entry.tags.all(),
        }


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
