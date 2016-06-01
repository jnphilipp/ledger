# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify


class TextFieldSingleLine(models.TextField):
    pass


class Category(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(unique=True)
    name = TextFieldSingleLine(unique=True)


    def get_absolute_url(self):
        return reverse('category', args=[self.slug])


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Category.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


    class Meta:
        ordering = ('name',)
        verbose_name = ' category'
        verbose_name_plural = ' categories'


class Tag(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(unique=True)
    name = TextFieldSingleLine(unique=True)


    def get_absolute_url(self):
        return reverse('tag', args=[self.slug])


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Tag.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


    class Meta:
        ordering = ('name',)
        verbose_name = ' tag'
        verbose_name_plural = ' tags'
