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
"""Portfolio Django app forms."""

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from ledger.dates import daterange
from units.models import Unit

from .models import Fund, Position, Stock


class PositionForm(forms.ModelForm):
    stock = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        required=False,
        label=_("Stock"),
    )
    fund = forms.ModelChoiceField(
        queryset=Fund.objects.all(),
        required=False,
        label=_("Fund"),
    )

    class Media:
        css = {"all": ("css/magnific-popup.css",)}
        js = ("js/jquery.magnific-popup.min.js",)

    class Meta:
        model = Position
        fields = ("closed", "trailing_stop_atr_factor")

    def __init__(self, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)

        self.fields["stock"].widget.attrs["style"] = "width: 100%;"
        self.fields["fund"].widget.attrs["style"] = "width: 100%;"

    def clean(self):
        cleaned_data = super().clean()

        stock = cleaned_data.get("stock")
        fund = cleaned_data.get("fund")
        if stock and fund:
            msg = "Only select on fo the two."
            self.add_error('stock', msg)
            self.add_error('fund', msg)
        else:
            if self.data["stock"] and "stock" not in cleaned_data:
                stock, created = Stock.objects.get_or_create(
                    name=self.data["stock"]
                )
                cleaned_data["stock"] = stock
                del self.errors["stock"]
            elif self.data["fund"] and "fund" not in cleaned_data:
                fund, created = Fund.objects.get_or_create(
                    name=self.data["fund"]
                )
                cleaned_data["fund"] = fund
                del self.errors["fund"]

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        stock = self.cleaned_data.get("stock")
        fund = self.cleaned_data.get("fund")

        if stock:
            instance.content_object = stock
        elif fund:
            instance.content_object = fund
        instance.save()

        # self.portfolio.positions.add(instance)
        return instance

    # def clean(self):
    #     cleaned_data = super().clean()

    #     if self.data["category"] and "category" not in cleaned_data:
    #         category, created = Category.objects.get_or_create(
    #             name=self.data["category"]
    #         )
    #         cleaned_data["category"] = category
    #         del self.errors["category"]

    #     if "tags" in self.data and self.data["tags"] and "tags" not in cleaned_data:
    #         tags = []
    #         for tag in self.data.getlist("tags"):
    #             if tag.isdigit():
    #                 tag = Tag.objects.get(pk=tag)
    #             else:
    #                 tag, created = Tag.objects.get_or_create(name=tag)
    #             tags.append(tag.pk)
    #         cleaned_data["tags"] = Tag.objects.filter(pk__in=tags)
    #         del self.errors["tags"]
