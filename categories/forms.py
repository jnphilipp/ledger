# -*- coding: utf-8 -*-

from categories.models import Category, Tag
from django import forms


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)


    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'autocomplete':'off', 'class':'form-control'})


    def is_valid(self):
        valid = super(CategoryForm, self).is_valid()
        if self.has_error('name', code='unique') and len(self.errors.as_data()) == 1:
            self._errors = ''
            return True
        return valid


    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        if Category.objects.filter(name=instance.name).exists():
            return Category.objects.get(name=instance.name)
        else:
            return super(CategoryForm, self).save(commit=commit)
