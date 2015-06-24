from django.conf import settings
from django.db import models

class Ledger(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	accounts = models.ManyToManyField('accounts.Account')

	def __str__(self):
		return 'ledger-%s' % self.user

	class Meta:
		ordering = ('user',)