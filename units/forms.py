# -*- coding: utf-8 -*-

from django import forms
from units.models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('name', 'symbol', 'precision')


    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control'})
        self.fields['symbol'].widget = forms.TextInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control'})
        self.fields['precision'].widget = forms.NumberInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control'})


    def is_valid(self):
        valid = super(UnitForm, self).is_valid()
        if self.has_error('name', code='unique') and self.has_error('symbol', code='unique') and len(self._errors.as_data()) == 2 and len(self._errors.as_data()['name']) <= 2:
            self._errors = ''
            return True
        return valid


    def save(self, commit=True):
        instance = super(UnitForm, self).save(commit=False)
        if Unit.objects.filter(name=instance.name).exists():
            return Unit.objects.get(name=instance.name)
        else:
            return super(UnitForm, self).save(commit=commit)
