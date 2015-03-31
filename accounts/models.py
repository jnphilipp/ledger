from app.models import Ledger
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

class TextFieldSingleLine(models.TextField):
	pass

class ReverseManyToManyField(models.ManyToManyField):
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

class Category(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	name = TextFieldSingleLine(unique=True)
	slug = models.SlugField(unique=True)

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
		verbose_name_plural = 'Categories'

class Tag(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	name = TextFieldSingleLine(unique=True)
	slug = models.SlugField(unique=True)

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

class Account(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	name = TextFieldSingleLine(unique=True)
	slug = models.SlugField(unique=True)
	balance = models.FloatField(default=0)
	unit = models.ForeignKey(Unit)
	ledgers = models.ManyToManyField(Ledger, blank=True, through=Ledger.accounts.through)

	def get_absolute_url(self):
		return reverse('account', args=[self.slug])

	def save(self, *args, **kwargs):
		self.balance = sum(entry.amount for entry in self.entry_set.all())
		if not self.slug:
			self.slug = slugify(self.name)
		else:
			orig = Account.objects.get(pk=self.id)
			if orig.name != self.name:
				self.slug = slugify(self.name)
		super(Account, self).save(*args, **kwargs)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('name',)

class Entry(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	account = models.ForeignKey(Account)
	serial_number = models.IntegerField()
	day = models.DateField()
	amount = models.FloatField(default=0)
	category = models.ForeignKey(Category)
	additional = TextFieldSingleLine(blank=True, null=True)
	tags = models.ManyToManyField(Tag, blank=True, null=True, related_name='entries')

	def save(self, *args, **kwargs):
		if not self.id:
			self.serial_number = Entry.objects.filter(account=self.account).last().serial_number + 1 if Entry.objects.filter(account=self.account).exists() else 1
		super(Entry, self).save()
		self.account.save()

	class Meta:
		ordering = ('account', 'serial_number')
		unique_together = ('account', 'serial_number')
		verbose_name_plural = 'Entries'