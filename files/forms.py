# -*- coding: utf-8 -*-

from accounts.models import Account
from django import forms
from files.models import Invoice, Statement
from django.utils.translation import ugettext_lazy as _


class InvoiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['uploader'].widget = forms.HiddenInput()
        self.fields['entry'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        entry = cleaned_data.get('entry')
        if Invoice.objects.filter(name=name).filter(invoice=invoice).exists():
            print('ValidationError')
            msg = _('An invoice with this name already exists for this entry.')
            self.add_error('name', forms.ValidationError(msg, code='invalid'))

    class Meta:
        model = Invoice
        fields = ('name', 'file', 'uploader', 'entry')


class StatementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StatementForm, self).__init__(*args, **kwargs)
        self.fields['uploader'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        account = cleaned_data.get('account')
        if Statement.objects.filter(name=name).filter(account=account). \
                exists():
            print('ValidationError')
            msg = _('A statement with this name already exists for this ' +
                    'account.')
            self.add_error('name', forms.ValidationError(msg, code='invalid'))

    class Meta:
        model = Statement
        fields = ('name', 'file', 'uploader', 'account')


class StatementFilterForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.all(),
                                              required=False)
