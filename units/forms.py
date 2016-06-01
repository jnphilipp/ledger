# -*- coding: utf-8 -*-

from django import forms
from units.models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('name', 'symbol', 'precision')

    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['symbol'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['precision'].widget = forms.NumberInput(attrs={'autocomplete':'off', 'class':'form-control'})
