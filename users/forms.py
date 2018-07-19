# -*- coding: utf-8 -*-

from categories.models import Tag
from django import forms
from django.contrib.auth import forms as authforms, get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from users.models import Budget


class AuthenticationForm(authforms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['password'].help_text = mark_safe(
            '<a href="%s">%s</a>' % (
                reverse('users:password_reset'),
                _('Forgot your password?')
            )
        )


class BudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.fields['income_tags'].empty_label = ''
        self.fields['income_tags'].queryset = Tag.objects.filter(
            entries__account__ledger__user=self.instance.user
        ).distinct()
        self.fields['income_tags'].widget.attrs['style'] = 'width: 100%;'

        self.fields['consumption_tags'].empty_label = ''
        self.fields['consumption_tags'].queryset = Tag.objects.filter(
            entries__account__ledger__user=self.instance.user
        ).distinct()
        self.fields['consumption_tags'].widget.attrs['style'] = 'width: 100%;'

        self.fields['insurance_tags'].empty_label = ''
        self.fields['insurance_tags'].queryset = Tag.objects.filter(
            entries__account__ledger__user=self.instance.user
        ).distinct()
        self.fields['insurance_tags'].widget.attrs['style'] = 'width: 100%;'

        self.fields['savings_tags'].empty_label = ''
        self.fields['savings_tags'].queryset = Tag.objects.filter(
            entries__account__ledger__user=self.instance.user
        ).distinct()
        self.fields['savings_tags'].widget.attrs['style'] = 'width: 100%;'

    class Meta:
        model = Budget
        fields = ('income_tags', 'consumption_tags', 'insurance_tags',
                  'savings_tags')


class PasswordChangeForm(authforms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = \
            mark_safe(self.fields['new_password1'].help_text)


class SetPasswordForm(authforms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1']. \
            help_text = mark_safe(self.fields['new_password1'].help_text)


class UserChangeForm(authforms.UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].help_text = mark_safe(
            self.fields['password'].help_text
        )

    class Meta(authforms.UserChangeForm.Meta):
        model = get_user_model()
        fields = ('username', 'password', 'email', 'first_name', 'last_name')


class UserCreationForm(authforms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].\
            help_text = mark_safe(self.fields['password1'].help_text)
