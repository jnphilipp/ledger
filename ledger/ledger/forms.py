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
"""Ledger Django app forms."""

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from units.models import Unit

from .dates import daterange
from .models import Account, Budget, Category, Entry, File, Tag
from .validators import validate_account_name


class AccountForm(forms.ModelForm):
    """Account form."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields["name"].validators = [validate_account_name]
        self.fields["category"].widget.attrs["style"] = "width: 100%;"
        self.fields["unit"].widget.attrs["style"] = "width: 100%;"

        if "instance" not in kwargs or kwargs["instance"] is None:
            self.fields["closed"].widget = forms.HiddenInput()

    def clean_name(self):
        """Clean name."""
        return self.cleaned_data["name"] or None

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()

        if self.data["category"] and "category" not in cleaned_data:
            category, created = Category.objects.get_or_create(
                name=self.data["category"]
            )
            cleaned_data["category"] = category
            del self.errors["category"]

    class Meta:
        """Meta."""

        model = Account
        fields = ("name", "closed", "category", "unit")


class EntryForm(forms.ModelForm):
    """Entry form."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(EntryForm, self).__init__(*args, **kwargs)

        self.fields["account"].widget.attrs["style"] = "width: 100%;"
        self.fields["category"].widget.attrs["style"] = "width: 100%;"
        self.fields["tags"].widget.attrs["style"] = "width: 100%;"

        self.fields["amount"].localize = True
        self.fields["amount"].widget = forms.TextInput(attrs={"step": "any"})
        self.fields["fees"].localize = True
        self.fields["fees"].widget = forms.TextInput(attrs={"step": "any"})

        self.fields["date"].help_text = mark_safe(
            '<a id="date_today" href="">%s</a> (%s)'
            % (_("Today"), _("Date format: yyyy-mm-dd"))
        )
        self.fields["date"].localize = True

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()

        if self.data["category"] and "category" not in cleaned_data:
            category, created = Category.objects.get_or_create(
                name=self.data["category"]
            )
            cleaned_data["category"] = category
            del self.errors["category"]

        if "tags" in self.data and self.data["tags"] and "tags" not in cleaned_data:
            tags = []
            for tag in self.data.getlist("tags"):
                if tag.isdigit():
                    tag = Tag.objects.get(pk=tag)
                else:
                    tag, created = Tag.objects.get_or_create(name=tag)
                tags.append(tag.pk)
            cleaned_data["tags"] = Tag.objects.filter(pk__in=tags)
            del self.errors["tags"]

    class Meta:
        """Meta."""

        model = Entry
        exclude = ["serial_number"]


class StandingEntryForm(forms.ModelForm):
    """Standing entry form."""

    start_date = forms.DateField(label=_("Start date"))
    end_date = forms.DateField(label=_("End date"))
    execution = forms.ChoiceField(
        choices=(
            (1, _("Monthly")),
            (2, _("Quarterly")),
            (3, _("Half-yearly")),
            (4, _("Yearly")),
        ),
        widget=forms.Select(attrs={"style": "width: 100%;"}),
        label=_("Execution"),
    )

    def __init__(self, *args, **kwargs):
        """Init."""
        super(StandingEntryForm, self).__init__(*args, **kwargs)

        self.fields["start_date"].help_text = mark_safe(_("Date format: yyyy-mm-dd"))
        self.fields["start_date"].localize = True
        self.fields["end_date"].help_text = mark_safe(_("Date format: yyyy-mm-dd"))
        self.fields["end_date"].localize = True

        self.fields["account"].widget.attrs["style"] = "width: 100%;"
        self.fields["category"].widget.attrs["style"] = "width: 100%;"
        self.fields["tags"].widget.attrs["style"] = "width: 100%;"

        self.fields["amount"].localize = True
        self.fields["amount"].widget = forms.TextInput(attrs={"step": "any"})
        self.fields["fees"].localize = True
        self.fields["fees"].widget = forms.TextInput(attrs={"step": "any"})

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()

        if self.data["category"] and "category" not in cleaned_data:
            category, created = Category.objects.get_or_create(
                name=self.data["category"]
            )
            cleaned_data["category"] = category
            del self.errors["category"]

        if "tags" in self.data and self.data["tags"] and "tags" not in cleaned_data:
            tags = []
            for tag in self.data.getlist("tags"):
                if tag.isdigit():
                    tag = Tag.objects.get(pk=tag)
                else:
                    tag, created = Tag.objects.get_or_create(name=tag)
                tags.append(tag.pk)
            cleaned_data["tags"] = Tag.objects.filter(pk__in=tags)
            del self.errors["tags"]

    def save(self, commit=True):
        """Save."""
        instance = super(StandingEntryForm, self).save(commit=False)
        entries = []
        start = self.cleaned_data["start_date"]
        end = self.cleaned_data["end_date"]
        for date in daterange(start, end, int(self.cleaned_data["execution"])):
            entry, created = Entry.objects.update_or_create(
                date=date,
                amount=instance.amount,
                fees=instance.fees,
                category=instance.category,
                text=instance.text,
                account=instance.account,
            )

            for tag in self.cleaned_data["tags"]:
                entry.tags.add(tag)
            entries.append(entry)
        return entries

    class Meta:
        """Meta."""

        model = Entry
        exclude = ["serial_number", "date"]
        fields = [
            "account",
            "start_date",
            "end_date",
            "execution",
            "amount",
            "fees",
            "category",
            "text",
            "tags",
        ]


class TransferForm(forms.Form):
    """Transfer form."""

    from_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(closed=False), label=_("From"), localize=True
    )
    from_date = forms.DateField(
        help_text=mark_safe(
            '<a id="from_date_today" href="">%s</a> (%s)'
            % (_("Today"), _("Date format: yyyy-mm-dd"))
        ),
        label=_("Date"),
    )
    to_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(closed=False), label=_("To"), localize=True
    )
    to_date = forms.DateField(
        help_text=mark_safe(
            '<a id="to_date_today" href="">%s</a> (%s)'
            % (_("Today"), _("Date format: yyyy-mm-dd"))
        ),
        label=_("Date"),
    )
    amount = forms.DecimalField(
        min_value=0.0, initial=0.0, label=_("Amount"), localize=True
    )
    fees = forms.DecimalField(
        min_value=0.0, initial=0.0, label=_("Fees"), localize=True
    )

    def __init__(self, *args, **kwargs):
        """Init."""
        super(TransferForm, self).__init__(*args, **kwargs)

        self.fields["from_account"].widget.attrs["style"] = "width: 100%;"
        self.fields["to_account"].widget.attrs["style"] = "width: 100%;"


class EntryFilterForm(forms.Form):
    """Entry filter form."""

    start_date = forms.DateField(
        localize=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Start date"),
            }
        ),
        required=False,
    )
    end_date = forms.DateField(
        localize=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("End date"),
            }
        ),
        required=False,
    )
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all(),
        required=False,
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )
    units = forms.ModelMultipleChoiceField(
        queryset=Unit.objects.all(),
        required=False,
    )


class FileForm(forms.ModelForm):
    """File form."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields["content_type"].widget = forms.HiddenInput()
        self.fields["object_id"].widget = forms.HiddenInput()

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        content_type = cleaned_data.get("content_type")
        object_id = cleaned_data.get("object_id")
        if (
            File.objects.filter(name=name)
            .filter(content_type=content_type)
            .filter(object_id=object_id)
            .exists()
        ):
            self.add_error(
                "name",
                forms.ValidationError(
                    _("A file with this name already exists."), code="invalid"
                ),
            )

    class Meta:
        """Meta."""

        model = File
        fields = ("name", "file", "content_type", "object_id")


class BudgetForm(forms.ModelForm):
    """Budget form."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.fields["income_tags"].empty_label = ""
        self.fields["income_tags"].queryset = Tag.objects.all()
        self.fields["income_tags"].widget.attrs["style"] = "width: 100%;"

        self.fields["consumption_tags"].empty_label = ""
        self.fields["consumption_tags"].queryset = Tag.objects.all()
        self.fields["consumption_tags"].widget.attrs["style"] = "width: 100%;"

        self.fields["insurance_tags"].empty_label = ""
        self.fields["insurance_tags"].queryset = Tag.objects.all()
        self.fields["insurance_tags"].widget.attrs["style"] = "width: 100%;"

        self.fields["savings_tags"].empty_label = ""
        self.fields["savings_tags"].queryset = Tag.objects.all()
        self.fields["savings_tags"].widget.attrs["style"] = "width: 100%;"

    class Meta:
        """Meta."""

        model = Budget
        fields = ("income_tags", "consumption_tags", "insurance_tags", "savings_tags")
