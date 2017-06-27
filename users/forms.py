# -*- coding: utf-8 -*-

from categories.models import Tag
from django import forms
from django.contrib.auth import forms as authforms, get_user_model
from django.utils.safestring import mark_safe
from users.models import Budget


class AuthenticationForm(authforms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ('income_tags', 'consumption_tags', 'insurance_tags', 'savings_tags')

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.fields['income_tags'].empty_label = ''
        self.fields['income_tags'].queryset = Tag.objects.filter(entries__account__ledger__user=self.instance.user).distinct()
        self.fields['income_tags'].widget.attrs['class'] = 'form-control js-example-basic-multiple'

        self.fields['consumption_tags'].empty_label = ''
        self.fields['consumption_tags'].queryset = Tag.objects.filter(entries__account__ledger__user=self.instance.user).distinct()
        self.fields['consumption_tags'].widget.attrs['class'] = 'form-control js-example-basic-multiple'

        self.fields['insurance_tags'].empty_label = ''
        self.fields['insurance_tags'].queryset = Tag.objects.filter(entries__account__ledger__user=self.instance.user).distinct()
        self.fields['insurance_tags'].widget.attrs['class'] = 'form-control js-example-basic-multiple'

        self.fields['savings_tags'].empty_label = ''
        self.fields['savings_tags'].queryset = Tag.objects.filter(entries__account__ledger__user=self.instance.user).distinct()
        self.fields['savings_tags'].widget.attrs['class'] = 'form-control js-example-basic-multiple'


class PasswordChangeForm(authforms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['new_password1'].help_text = mark_safe(self.fields['new_password1'].help_text)
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})


class PasswordResetForm(authforms.PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={'autocomplete': 'off', 'class': 'form-control'})


class SetPasswordForm(authforms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = mark_safe(self.fields['new_password1'].help_text)
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})


class UserChangeForm(authforms.UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['email'].widget = forms.EmailInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['first_name'].widget = forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['last_name'].widget = forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['password'].help_text = mark_safe(self.fields['password'].help_text)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'email', 'first_name', 'last_name')


class UserCreationForm(authforms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['password1'].help_text = mark_safe(self.fields['password1'].help_text)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'off', 'class': 'form-control'})
