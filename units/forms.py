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

from django import forms

from .models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ("name", "symbol", "precision")

    def is_valid(self):
        valid = super(UnitForm, self).is_valid()
        if self.has_error("name", code="unique"):
            if self.has_error("symbol", code="unique"):
                if len(self._errors.as_data()) == 2:
                    if len(self._errors.as_data()["name"]) <= 2:
                        self.cleaned_data["name"] = self.instance.name
                        self.cleaned_data["symbol"] = self.instance.symbol
                        self._errors = ""
                        return True
        return valid

    def save(self, commit=True):
        instance = super(UnitForm, self).save(commit=False)
        if Unit.objects.filter(name=instance.name).exists():
            return Unit.objects.get(name=instance.name)
        else:
            return super(UnitForm, self).save(commit=commit)
