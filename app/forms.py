from django import forms
from django.contrib.auth.forms import AuthenticationForm

class AuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'username'
        self.fields['username'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control', 'placeholder':'username'})
        self.fields['password'].label = 'password'
        self.fields['password'].widget = forms.PasswordInput(attrs={'autocomplete':'off', 'class':'form-control', 'placeholder':'password'})