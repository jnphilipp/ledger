# -*- coding: utf-8 -*-

from django import forms
from units.models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('name', 'symbol', 'precision')

    def is_valid(self):
        valid = super(UnitForm, self).is_valid()
        if self.has_error('name', code='unique'):
            if self.has_error('symbol', code='unique'):
                if len(self._errors.as_data()) == 2:
                   if len(self._errors.as_data()['name']) <= 2:
                        self._errors = ''
                        return True
        return valid

    def save(self, commit=True):
        instance = super(UnitForm, self).save(commit=False)
        if Unit.objects.filter(name=instance.name).exists():
            return Unit.objects.get(name=instance.name)
        else:
            return super(UnitForm, self).save(commit=commit)
