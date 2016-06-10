# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import forms as authforms, get_user_model
from django.utils.safestring import mark_safe


class AuthenticationForm(authforms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'username'
        self.fields['username'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control', 'placeholder':'username'})
        self.fields['password'].label = 'password'
        self.fields['password'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control', 'placeholder':'password'})


class PasswordChangeForm(authforms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['new_password1'].help_text = mark_safe(self.fields['new_password1'].help_text)
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control'})


class PasswordResetForm(authforms.PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={'autocomplete':'off', 'class':'form-control'})


class SetPasswordForm(authforms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = mark_safe(self.fields['new_password1'].help_text)
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control'})


class UserChangeForm(authforms.UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['email'].widget = forms.EmailInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['first_name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['last_name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['password'].help_text = mark_safe(self.fields['password'].help_text)


    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'email', 'first_name', 'last_name')


class UserCreationForm(authforms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control'})
