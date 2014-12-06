from django.db import models
from django.template.defaultfilters import slugify

class TextFieldSingleLine(models.TextField):
	pass

class Unit(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	name = TextFieldSingleLine(unique=True)
	slug = models.SlugField(unique=True)
	symbol = TextFieldSingleLine(unique=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		else:
			orig = Unit.objects.get(pk=self.id)
			if orig.name != self.name:
				self.slug = slugify(self.name)
		super(Unit, self).save(*args, **kwargs)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('name',)