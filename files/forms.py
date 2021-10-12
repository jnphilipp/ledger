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
from django import forms
from files.models import Invoice, Statement
from django.utils.translation import gettext_lazy as _


class InvoiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        # self.fields["uploader"].widget = forms.HiddenInput()
        self.fields["entry"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        entry = cleaned_data.get("entry")
        if Invoice.objects.filter(name=name).filter(entry=entry).exists():
            print("ValidationError")
            msg = _("An invoice with this name already exists for this entry.")
            self.add_error("name", forms.ValidationError(msg, code="invalid"))

    class Meta:
        model = Invoice
        fields = ("name", "file", "entry")


class StatementForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(StatementForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        account = cleaned_data.get("account")
        if Statement.objects.filter(name=name).filter(account=account).exists():
            print("ValidationError")
            msg = _("A statement with this name already exists for this " + "account.")
            self.add_error("name", forms.ValidationError(msg, code="invalid"))

    class Meta:
        model = Statement
        fields = ("name", "file", "account")


class StatementFilterForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all(), required=False
    )
