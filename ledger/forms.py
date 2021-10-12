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

from categories.models import Tag
from django import forms

from .models import Budget


class BudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
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
        model = Budget
        fields = ("income_tags", "consumption_tags", "insurance_tags", "savings_tags")
