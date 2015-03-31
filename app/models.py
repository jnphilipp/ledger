from django.contrib.auth.models import User
from django.db import models

class Ledger(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	user = models.ForeignKey(User)
	accounts = models.ManyToManyField('accounts.Account', blank=True)

	def __str__(self):
		return 'ledger-%s' % self.user

	class Meta:
		ordering = ('user',)