# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from django import forms
from files.models import File
from django.utils.translation import ugettext_lazy as _


class FileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['uploader'].widget = forms.HiddenInput()
        self.fields['content_type'].widget = forms.HiddenInput()
        self.fields['object_id'].widget = forms.HiddenInput()

    class Meta:
        model = File
        fields = ('name', 'file', 'uploader', 'content_type', 'object_id')
