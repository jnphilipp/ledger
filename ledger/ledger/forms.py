# Copyright (C) 2014-2024 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
        super().__init__(*args, **kwargs)
        self.fields["name"].validators = [validate_account_name]

        if "instance" not in kwargs or kwargs["instance"] is None:
            self.fields["closed"].widget = forms.HiddenInput()

    def clean_name(self):
        """Clean name."""
        return self.cleaned_data["name"] or None

    class Meta:
        """Meta."""

        model = Account
        fields = ("name", "closed", "unit")


class EntryForm(forms.ModelForm):
    """Entry form."""

    intervall = forms.ChoiceField(
        choices=(
            (0, _("Never")),
            (1, _("Monthly")),
            (2, _("Bimonthly")),
            (3, _("Quarterly")),
            (4, _("Half-yearly")),
            (5, _("Yearly")),
        ),
        widget=forms.Select(),
        initial=0,
        label=_("Repeat intervall"),
        required=False,
    )
    end_date = forms.DateField(label=_("End date"), required=False)

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        if "instance" in kwargs and kwargs["instance"] is not None:
            del self.fields["intervall"]
            del self.fields["end_date"]
            self.fields["related"].queryset = Entry.objects.filter(
                pk__in=[
                    kwargs["instance"].pk,
                    (
                        kwargs["instance"].related.pk
                        if kwargs["instance"].related is not None
                        else None
                    ),
                ]
            )
        else:
            del self.fields["related"]

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

        if "related" in self.errors:
            try:
                entry = Entry.objects.get(pk=self.data["related"])
                cleaned_data["related"] = entry
                del self.errors["related"]
            except Entry.DoesNotExist:
                pass

        if "intervall" in cleaned_data and "end_date" in cleaned_data:
            intervall = cleaned_data["intervall"]
            end_date = cleaned_data["end_date"]
            if (int(intervall) > 0 and end_date is None) or (
                int(intervall) == 0 and end_date is not None
            ):
                msg = _("Repeat intervall and end date need both be set.")
                self.add_error("intervall", msg)
                self.add_error("end_date", msg)

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

    def save(self, commit: bool = True):
        """Save."""
        instance = super().save(commit=False)

        date = self.cleaned_data["date"]
        intervall = (
            self.cleaned_data["intervall"] if "intervall" in self.cleaned_data else 0
        )
        end_date = (
            self.cleaned_data["end_date"] if "end_date" in self.cleaned_data else None
        )

        if int(intervall) == 0 and end_date is None:
            if instance.pk is None:
                try:
                    instance.save()
                    self.save_m2m()
                    account = Account.objects.get(category__pk=instance.category.pk)
                    entry, created = Entry.objects.update_or_create(
                        date=instance.date,
                        amount=-1.0 * instance.amount,
                        fees=instance.fees,
                        category=instance.account.category,
                        text=instance.text,
                        account=account,
                        related=instance,
                    )
                    instance.related = entry
                    instance.save()
                    for tag in self.cleaned_data["tags"]:
                        entry.tags.add(tag)
                    return [instance, entry]
                except Account.DoesNotExist:
                    return instance
            else:
                instance.save()
                self.save_m2m()
                if instance.related is not None:
                    if instance.account.unit == instance.related.account.unit:
                        instance.related.amount = -1.0 * instance.amount
                    try:
                        instance.related.account = Account.objects.get(
                            category__pk=instance.category.pk
                        )
                    except Account.DoesNotExist:
                        pass
                    instance.related.category = instance.account.category
                    instance.related.save()
                return instance
        else:
            entries = []
            try:
                account = Account.objects.get(category__pk=instance.category.pk)
            except Account.DoesNotExist:
                account = None
            for cur_date in daterange(date, end_date, "months", int(intervall)):
                entry, created = Entry.objects.update_or_create(
                    date=cur_date,
                    amount=instance.amount,
                    fees=instance.fees,
                    category=instance.category,
                    text=instance.text,
                    account=instance.account,
                )
                for tag in self.cleaned_data["tags"]:
                    entry.tags.add(tag)
                entries.append(entry)

                if account is not None:
                    entry, created = Entry.objects.update_or_create(
                        date=cur_date,
                        amount=-1.0 * instance.amount,
                        fees=instance.fees,
                        category=instance.account.category,
                        text=instance.text,
                        account=account,
                        related=entries[-1],
                    )
                    entries[-1].related = entry
                    entries[-1].save()
                    for tag in self.cleaned_data["tags"]:
                        entry.tags.add(tag)
                    entries.append(entry)
            return entries

    class Meta:
        """Meta."""

        model = Entry
        exclude = ["serial_number"]


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

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        self.fields["accounts"].widget.attrs[
            "style"
        ] = "min-width: 113px !important; max-width: 227px !important;"
        self.fields["categories"].widget.attrs[
            "style"
        ] = "min-width: 113px !important; max-width: 227px !important;"
        self.fields["tags"].widget.attrs[
            "style"
        ] = "min-width: 113px !important; max-width: 227px !important;"
        self.fields["units"].widget.attrs[
            "style"
        ] = "min-width: 113px !important; max-width: 227px !important;"

        if Tag.objects.count() == 0:
            del self.fields["tags"]


class FileForm(forms.ModelForm):
    """File form."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
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
        super().__init__(*args, **kwargs)
        self.fields["income_tags"].empty_label = ""
        self.fields["income_tags"].queryset = Tag.objects.all()

        self.fields["consumption_tags"].empty_label = ""
        self.fields["consumption_tags"].queryset = Tag.objects.all()

        self.fields["insurance_tags"].empty_label = ""
        self.fields["insurance_tags"].queryset = Tag.objects.all()

        self.fields["savings_tags"].empty_label = ""
        self.fields["savings_tags"].queryset = Tag.objects.all()

    class Meta:
        """Meta."""

        model = Budget
        fields = ("income_tags", "consumption_tags", "insurance_tags", "savings_tags")
