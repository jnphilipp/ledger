# -*- coding: utf-8 -*-

from categories.models import Category, Tag
from django import forms
from django.utils.translation import ugettext_lazy as _


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def is_valid(self):
        valid = super(CategoryForm, self).is_valid()
        if self.has_error('name', code='unique'):
            if len(self._errors.as_data()) == 1:
                if len(self._errors.as_data()['name']) == 1:
                    self.cleaned_data['name'] = self.instance.name
                    self._errors = ''
                    return True
        return valid

    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        if Category.objects.filter(name=instance.name).exists():
            return Category.objects.get(name=instance.name)
        else:
            return super(CategoryForm, self).save(commit=commit)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name',)

    def is_valid(self):
        valid = super(TagForm, self).is_valid()
        if self.has_error('name', code='unique'):
            if len(self._errors.as_data()) == 1:
                if len(self._errors.as_data()['name']) == 1:
                    self.cleaned_data['name'] = self.instance.name
                    self._errors = ''
                    return True
        return valid

    def save(self, commit=True):
        instance = super(TagForm, self).save(commit=False)
        if Tag.objects.filter(name=instance.name).exists():
            return Tag.objects.get(name=instance.name)
        else:
            return super(TagForm, self).save(commit=commit)
