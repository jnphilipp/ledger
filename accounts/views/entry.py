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

import csv

from accounts.forms import EntryForm, EntryFilterForm
from accounts.models import Account, Entry
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import floatformat
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from ledger.dates import get_last_date_current_month
from users.models import Ledger


@method_decorator(login_required, name="dispatch")
class ListView(generic.ListView):
    context_object_name = "entries"
    model = Entry
    paginate_by = 200

    def get_queryset(self):
        self.form = EntryFilterForm(self.request.GET)
        if "slug" in self.kwargs:
            self.account = get_object_or_404(Account, slug=self.kwargs["slug"])
            del self.form.fields["accounts"]
            del self.form.fields["units"]
            entries = (
                Entry.objects.filter(account__ledger__user=self.request.user)
                .filter(account__slug=self.kwargs["slug"])
                .order_by("-serial_number")
            )
        else:
            self.account = None
            entries = Entry.objects.filter(
                account__ledger__user=self.request.user
            ).order_by("-day", "account__name", "-serial_number")

        filtered = False
        self.start_date = None
        self.end_date = None
        self.accounts = []
        self.categories = []
        self.tags = []
        self.units = []
        if self.form.is_valid():
            if self.form.cleaned_data["start_date"]:
                filtered = True
                self.start_date = self.form.cleaned_data["start_date"]
                entries = entries.filter(day__gte=self.start_date)
            if self.form.cleaned_data["end_date"]:
                filtered = True
                self.end_date = self.form.cleaned_data["end_date"]
                entries = entries.filter(day__lte=self.end_date)
            if (
                "accounts" in self.form.cleaned_data
                and self.form.cleaned_data["accounts"]
            ):
                filtered = True
                self.accounts = [a.pk for a in self.form.cleaned_data["accounts"]]
                entries = entries.filter(account__in=self.accounts)
            if self.form.cleaned_data["categories"]:
                filtered = True
                self.categories = [c.pk for c in self.form.cleaned_data["categories"]]
                entries = entries.filter(category__in=self.categories)
            if self.form.cleaned_data["tags"]:
                filtered = True
                self.tags = [t.pk for t in self.form.cleaned_data["tags"]]
                entries = entries.filter(tags__in=self.tags)
            if "units" in self.form.cleaned_data and self.form.cleaned_data["units"]:
                filtered = True
                self.units = [u.pk for u in self.form.cleaned_data["units"]]
                entries = entries.filter(account__unit__in=self.units)

        if not filtered:
            self.end_date = get_last_date_current_month()
            self.form = EntryFilterForm(initial={"end_date": self.end_date})
            entries = entries.filter(day__lte=self.end_date)

            if "slug" in self.kwargs:
                del self.form.fields["accounts"]
                del self.form.fields["units"]

        entries = entries.annotate(total=F("amount") + F("fees"))
        return entries.distinct()

    def get_context_data(self, *args, **kwargs):
        context = super(ListView, self).get_context_data(*args, **kwargs)

        context["form"] = self.form
        context["start_date"] = self.start_date
        context["end_date"] = self.end_date
        context["accounts"] = self.accounts
        context["categories"] = self.categories
        context["tags"] = self.tags
        context["units"] = self.units
        if "slug" in self.kwargs:
            context["account"] = self.account
            context["show_options"] = not context["account"].closed
        else:
            context["show_options"] = True

        return context


@method_decorator(login_required, name="dispatch")
class DetailView(generic.DetailView):
    model = Entry

    def get_object(self, queryset=None):
        if "slug" in self.kwargs and self.kwargs["slug"]:
            return Entry.objects.get(
                account__slug=self.kwargs["slug"], pk=self.kwargs["pk"]
            )
        else:
            return Entry.objects.get(pk=self.kwargs["pk"])


@method_decorator(login_required, name='dispatch')
class CSVExportView(ListView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="entries.csv"'},
        )

        writer = csv.writer(response, dialect="unix")
        writer.writerow([_("Account"), _("Day"), _("Amount"), _("Category"), _("Additional"), _("Tags")])
        for entry in self.get_queryset():
            precision = entry.account.unit.precision if entry.account.unit else 2
            symbol = entry.account.unit.symbol if entry.account.unit else ""

            writer.writerow([
                f"{entry.account.name} #{entry.serial_number}",
                entry.day,
                f"{floatformat(entry.total, precision)} {symbol}".strip() if entry.total else f'{floatformat(0, precision)} {symbol}'.strip(),
                entry.category.name,
                entry.additional if entry.additional else "",
                ", ".join([tag.name for tag in entry.tags.all()])
            ])

        return response


@method_decorator(login_required, name="dispatch")
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = EntryForm
    model = Entry
    success_message = _('The entry "%(entry)s" was successfully created.')

    def get_initial(self):
        initial = {"ledger": self.request.user.ledger}
        if "slug" in self.kwargs:
            initial["account"] = get_object_or_404(Account, slug=self.kwargs["slug"])
        return initial

    def get_success_message(self, cleaned_data):
        entry = "%s - #%s" % (self.object.account.name, self.object.serial_number)
        return self.success_message % {"entry": entry}

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
    form_class = EntryForm
    model = Entry

    def form_valid(self, form):
        self.orig_serial_number = self.object.serial_number
        return super(UpdateView, self).form_valid(form)

    def get_initial(self):
        return {
            "ledger": self.request.user.ledger,
            "show_account": "slug" not in self.kwargs,
        }

    def get_queryset(self):
        return Entry.objects.filter(account__ledger__user=self.request.user)

    def get_success_message(self, cleaned_data):
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
    model = Entry

    def delete(self, request, *args, **kwargs):
        v = super(DeleteView, self).delete(request, *args, **kwargs)
        for entry in Entry.objects.filter(account=self.object.account).filter(
            serial_number__gt=self.object.serial_number
        ):
            entry.serial_number -= 1
            entry.save()
        self.object.account.save()
        return v

    def get_queryset(self):
        return Entry.objects.filter(account__ledger__user=self.request.user)

    def get_success_url(self):
        msg = _('The entry "%(entry)s" was successfully deleted.')
        msg %= {
            "entry": "%s - #%s" % (self.object.account.name, self.object.serial_number)
        }
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


@method_decorator(login_required, name="dispatch")
class DuplicateView(generic.base.RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        ledger = get_object_or_404(Ledger, user=self.request.user)

        if "slug" in kwargs:
            account = get_object_or_404(Account, slug=kwargs["slug"], ledger=ledger)
            entry = get_object_or_404(Entry, pk=kwargs["pk"], account=account)
        else:
            account = None
            entry = get_object_or_404(Entry, pk=kwargs["pk"])

        new = Entry.objects.create(
            account=entry.account,
            day=date.today(),
            amount=entry.amount,
            fees=entry.fees,
            category=entry.category,
            additional=entry.additional,
        )
        for tag in entry.tags.all():
            new.tags.add(tag.id)
        new.save()

        msg = _(
            'The entry "%(old_entry)s" has been successfully duplicated '
            + 'as entry "%(new_entry)s".'
        )
        if account:
            old_entry = "#%s" % entry.serial_number
            new_entry = "#%s" % new.serial_number
            msg %= {"old_entry": old_entry, "new_entry": new_entry}
            self.url = reverse_lazy(
                "accounts:account_entry_list", args=[kwargs["slug"]]
            )
        else:
            old_entry = "%s - #%s" % (entry.account.name, entry.serial_number)
            new_entry = "%s - #%s" % (new.account.name, new.serial_number)
            msg %= {"old_entry": old_entry, "new_entry": new_entry}
            self.url = reverse_lazy("accounts:entry_list")
        messages.add_message(self.request, messages.SUCCESS, msg)
        return super().get_redirect_url(*args, **kwargs)


@method_decorator(login_required, name="dispatch")
class SwapView(generic.base.RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        ledger = get_object_or_404(Ledger, user=self.request.user)
        if "slug" in kwargs:
            account = get_object_or_404(Account, slug=kwargs["slug"], ledger=ledger)
            e1 = get_object_or_404(Entry, id=kwargs["pk"], account=account)
        else:
            e1 = get_object_or_404(Entry, id=kwargs["pk"], account__ledger=ledger)

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
            msg %= {"e1": e1.serial_number, "e2": e2.serial_number}
            messages.add_message(self.request, messages.SUCCESS, msg)

        if "slug" in kwargs:
            self.url = reverse_lazy(
                "accounts:account_entry_list", args=[kwargs["slug"]]
            )
        else:
            self.url = reverse_lazy("accounts:entry_list")
        return super().get_redirect_url(*args, **kwargs)
