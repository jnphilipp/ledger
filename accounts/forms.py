# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from accounts.validators import validate_account_name
from categories.models import Category, Tag
from datetime import datetime
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from ledger.functions.dates import daterange
from units.models import Unit


class AccountForm(forms.ModelForm):
    class Media:
        css = {
            'all': ('css/magnific-popup.css',)
        }
        js = ('js/jquery.magnific-popup.min.js',)


    class Meta:
        model = Account
        fields = ('name', 'category', 'unit')


    def __init__(self, ledger, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['name'].validators = [validate_account_name]

        self.fields['category'].empty_label = ''
        self.fields['category'].help_text = mark_safe('<a href="%s" class="ajax-popup-link"><span class="glyphicon glyphicon-plus text-success"></span></a>' % reverse('category_add_another'))
        self.fields['category'].queryset = Category.objects.filter(Q(entries__account__ledger=ledger) | Q(accounts__ledger=ledger)).distinct()
        self.fields['category'].widget.attrs['class'] = 'form-control js-example-basic-single'
        self.fields['category'].widget.attrs['style'] = 'width: 95%;'

        self.fields['unit'].empty_label = ''
        self.fields['unit'].queryset = Unit.objects.filter(accounts__ledger=ledger).distinct()
        self.fields['unit'].widget.attrs['class'] = 'form-control js-example-basic-single'
        self.fields['unit'].widget.attrs['style'] = 'width: 95%;'
        self.fields['unit'].help_text = mark_safe('<a href="%s" class="ajax-popup-link"><span class="glyphicon glyphicon-plus text-success"></span></a>' % reverse('unit_add_another'))


class EntryForm(forms.ModelForm):
    class Media:
        css = {
            'all': ('css/magnific-popup.css',)
        }
        js = ('js/jquery.magnific-popup.min.js',)


    class Meta:
        model = Entry
        exclude = ['serial_number']


    def __init__(self, ledger, exclude_account=True, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        if exclude_account:
            del self.fields['account']
        else:
            self.fields['account'].empty_label = ''
            self.fields['account'].queryset = ledger.accounts.all()
            self.fields['account'].widget.attrs['class'] = 'form-control js-example-basic-multiple'

        self.fields['additional'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['amount'].widget = forms.TextInput(attrs={'step':'any', 'autocomplete':'off', 'class':'form-control'})

        self.fields['day'].help_text = mark_safe('<a id="date_today" style="cursor: pointer;">today</a> (%s: yyyy-mm-dd)' % _('date format'))
        self.fields['day'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})

        self.fields['category'].empty_label = ''
        self.fields['category'].help_text = mark_safe('<a href="%s" class="ajax-popup-link"><span class="glyphicon glyphicon-plus text-success"></span></a>' % reverse('category_add_another'))
        self.fields['category'].queryset = Category.objects.filter(Q(entries__account__ledger=ledger) | Q(accounts__ledger=ledger)).distinct()
        self.fields['category'].widget.attrs['class'] = 'form-control js-example-basic-single'
        self.fields['category'].widget.attrs['style'] = 'width: 95%;'

        self.fields['tags'].empty_label = ''
        self.fields['tags'].help_text = mark_safe('<a href="%s" class="ajax-popup-link"><span class="glyphicon glyphicon-plus text-success"></span></a>' % reverse('tag_add_another'))
        self.fields['tags'].queryset = Tag.objects.filter(entries__account__ledger=ledger).distinct()
        self.fields['tags'].widget.attrs['class'] = 'form-control js-example-basic-multiple'
        self.fields['tags'].widget.attrs['style'] = 'width: 95%;'


class StandingEntryForm(forms.ModelForm):
    start_date = forms.CharField(widget=forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'}))
    end_date = forms.CharField(widget=forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'}))
    execution = forms.ChoiceField(choices=((1, _('monthly')), (2, _('quarterly')), (3, _('half-yearly')), (4, _('yearly'))), widget=forms.Select(attrs={'class':'form-control js-example-basic-hide-search'}))


    class Media:
        css = {
            'all': ('css/magnific-popup.css',)
        }
        js = ('js/jquery.magnific-popup.min.js',)


    class Meta:
        model = Entry
        exclude = ['serial_number', 'day']
        fields = ['account', 'start_date', 'end_date', 'execution', 'amount', 'category', 'additional', 'tags']


    def __init__(self, ledger, exclude_account=True, *args, **kwargs):
        super(StandingEntryForm, self).__init__(*args, **kwargs)
        if exclude_account:
            del self.fields['account']
        else:
            self.fields['account'].empty_label = ''
            self.fields['account'].queryset = ledger.accounts.all()
            self.fields['account'].widget.attrs['class'] = 'form-control js-example-basic-multiple'

        self.fields['additional'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['amount'].widget = forms.TextInput(attrs={'step':'any', 'autocomplete':'off', 'class':'form-control'})

        self.fields['category'].empty_label = ''
        self.fields['category'].help_text = mark_safe('<a href="%s" class="ajax-popup-link"><span class="glyphicon glyphicon-plus text-success"></span></a>' % reverse('category_add_another'))
        self.fields['category'].queryset = Category.objects.filter(Q(entries__account__ledger=ledger) | Q(accounts__ledger=ledger)).distinct()
        self.fields['category'].widget.attrs['class'] = 'form-control js-example-basic-single'
        self.fields['category'].widget.attrs['style'] = 'width: 95%;'

        self.fields['tags'].empty_label = ''
        self.fields['tags'].help_text = mark_safe('<a href="%s" class="ajax-popup-link"><span class="glyphicon glyphicon-plus text-success"></span></a>' % reverse('tag_add_another'))
        self.fields['tags'].queryset = Tag.objects.filter(entries__account__ledger=ledger).distinct()
        self.fields['tags'].widget.attrs['class'] = 'form-control js-example-basic-multiple'
        self.fields['tags'].widget.attrs['style'] = 'width: 95%;'


    def save(self, commit=True):
        instance = super(StandingEntryForm, self).save(commit=False)
        entries = []
        start = datetime.strptime(self.cleaned_data['start_date'], '%Y-%m-%d').date()
        end = datetime.strptime(self.cleaned_data['end_date'], '%Y-%m-%d').date()
        for date in daterange(start, end, int(self.cleaned_data['execution'])):
            entry, created = Entry.objects.update_or_create(day=date, amount=instance.amount, category=instance.category, additional=instance.additional, account=instance.account)
            for tag in self.cleaned_data['tags']: entry.tags.add(tag)
            entries.append(entry)
        return entries


class EntryFilterForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'start date', 'class':'form-control'}), required=False)
    end_date = forms.DateField(widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'end date', 'class':'form-control'}), required=False)
    accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class':'form-control js-example-basic-multiple', 'style':'width: 200px;'}))
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class':'form-control js-example-basic-multiple', 'style':'width: 200px;'}))
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class':'form-control js-example-basic-multiple', 'style':'width: 200px;'}))
    units = forms.ModelMultipleChoiceField(queryset=Unit.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class':'form-control js-example-basic-multiple', 'style':'width: 200px;'}))
