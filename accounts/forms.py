# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from accounts.validators import validate_account_name
from categories.models import Category, Tag
from datetime import datetime
from django import forms
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from ledger.dates import daterange
from units.models import Unit


class AccountForm(forms.ModelForm):
    class Media:
        css = {
            'all': ('css/magnific-popup.css',)
        }
        js = ('js/jquery.magnific-popup.min.js',)

    class Meta:
        model = Account
        fields = ('name', 'category', 'unit', 'closed')

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['name'].validators = [validate_account_name]
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].widget.attrs['style'] = 'width: 100%;'
        self.fields['unit'].queryset = Unit.objects.all()
        self.fields['unit'].widget.attrs['style'] = 'width: 100%;'

        if 'instance' not in kwargs or kwargs['instance'] is None:
            self.fields['closed'].widget = forms.HiddenInput()

    def clean_name(self):
        return self.cleaned_data['name'] or None


class EntryForm(forms.ModelForm):
    class Media:
        css = {
            'all': ('css/magnific-popup.css',)
        }
        js = ('js/jquery.magnific-popup.min.js',)

    class Meta:
        model = Entry
        exclude = ['serial_number']

    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)

        if 'ledger' in kwargs:
            ledger = kwargs['ledger']
        elif 'initial' in kwargs and 'ledger' in kwargs['initial']:
            ledger = kwargs['initial']['ledger']

        self.fields['account'].queryset = ledger.accounts.filter(closed=False)
        self.fields['account'].widget.attrs['style'] = 'width: 100%;'
        self.fields['amount'].widget = forms.TextInput(attrs={'step': 'any'})
        self.fields['fees'].widget = forms.TextInput(attrs={'step': 'any'})
        self.fields['day'].help_text = \
            mark_safe('<a id="date_today" href="">%s</a> (%s: yyyy-mm-dd)' %
                      (_('Today'), _('Date format')))
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].widget.attrs['style'] = 'width: 100%;'
        self.fields['tags'].queryset = Tag.objects.all()
        self.fields['tags'].widget.attrs['style'] = 'width: 100%;'

    def clean(self):
        cleaned_data = super().clean()

        if self.data['category'] and 'category' not in cleaned_data:
            category, created = Category.objects.get_or_create(
                name=self.data['category'])
            cleaned_data['category'] = category
            del self.errors['category']

        if 'tags' in self.data and self.data['tags'] and \
                'tags' not in cleaned_data:
            tags = []
            for tag in self.data.getlist('tags'):
                if tag.isdigit():
                    tag = Tag.objects.get(pk=tag)
                else:
                    tag, created = Tag.objects.get_or_create(name=tag)
                tags.append(tag.pk)
            cleaned_data['tags'] = Tag.objects.filter(pk__in=tags)
            del self.errors['tags']


class StandingEntryForm(forms.ModelForm):
    start_date = forms.DateField(label=_('Start date'))
    end_date = forms.DateField(label=_('End date'))
    execution = forms.ChoiceField(
        choices=((1, _('Monthly')), (2, _('Quarterly')), (3, _('Half-yearly')),
                 (4, _('Yearly'))),
        widget=forms.Select(attrs={'style': 'width: 100%;'}),
        label=_('Execution')
    )

    class Media:
        css = {
            'all': ('css/magnific-popup.css',)
        }
        js = ('js/jquery.magnific-popup.min.js',)

    class Meta:
        model = Entry
        exclude = ['serial_number', 'day']
        fields = ['account', 'start_date', 'end_date', 'execution', 'amount',
                  'fees', 'category', 'additional', 'tags']

    def __init__(self, *args, **kwargs):
        super(StandingEntryForm, self).__init__(*args, **kwargs)

        if 'ledger' in kwargs:
            ledger = kwargs['ledger']
        elif 'initial' in kwargs and 'ledger' in kwargs['initial']:
            ledger = kwargs['initial']['ledger']

        self.fields['start_date'].help_text = mark_safe(
            f'{_("Date format")}: yyyy-mm-dd')
        self.fields['end_date'].help_text = mark_safe(
            f'{_("Date format")}: yyyy-mm-dd')

        self.fields['account'].queryset = ledger.accounts.filter(closed=False)
        self.fields['account'].widget.attrs['style'] = 'width: 100%;'
        self.fields['amount'].widget = forms.TextInput(attrs={'step': 'any'})
        self.fields['fees'].widget = forms.TextInput(attrs={'step': 'any'})
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].widget.attrs['style'] = 'width: 100%;'
        self.fields['tags'].queryset = Tag.objects.all()
        self.fields['tags'].widget.attrs['style'] = 'width: 100%;'

    def clean(self):
        cleaned_data = super().clean()

        if self.data['category'] and 'category' not in cleaned_data:
            category, created = Category.objects.get_or_create(
                name=self.data['category'])
            cleaned_data['category'] = category
            del self.errors['category']

        if 'tags' in self.data and self.data['tags'] and \
                'tags' not in cleaned_data:
            tags = []
            for tag in self.data.getlist('tags'):
                if tag.isdigit():
                    tag = Tag.objects.get(pk=tag)
                else:
                    tag, created = Tag.objects.get_or_create(name=tag)
                tags.append(tag.pk)
            cleaned_data['tags'] = Tag.objects.filter(pk__in=tags)
            del self.errors['tags']

    def save(self, commit=True):
        instance = super(StandingEntryForm, self).save(commit=False)
        entries = []
        start = datetime.strptime(self.cleaned_data['start_date'],
                                  '%Y-%m-%d').date()
        end = datetime.strptime(self.cleaned_data['end_date'],
                                '%Y-%m-%d').date()
        for date in daterange(start, end, int(self.cleaned_data['execution'])):
            entry, created = Entry.objects.update_or_create(
                day=date,
                amount=instance.amount,
                fees=instance.fees,
                category=instance.category,
                additional=instance.additional,
                account=instance.account
            )

            for tag in self.cleaned_data['tags']:
                entry.tags.add(tag)
            entries.append(entry)
        return entries


class EntryFilterForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={
            'placeholder': _('Start date'),
            'style': 'width: 250px;'
        }),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={
            'placeholder': _('End date'),
            'style': 'width: 250px;'
        }),
        required=False
    )
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'style': 'width: 250px;'})
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'style': 'width: 250px;'})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'style': 'width: 250px;'})
    )
    units = forms.ModelMultipleChoiceField(
        queryset=Unit.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'style': 'width: 250px;'})
    )
