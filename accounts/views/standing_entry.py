# -*- coding: utf-8 -*-

from accounts.forms import StandingEntryForm
from accounts.models import Account, Entry
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views import generic


@method_decorator(login_required, name='dispatch')
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = StandingEntryForm
    model = Entry
    success_message = _('The entries %(entries)s were successfully created.')

    def get_context_data(self, *args, **kwargs):
        context = super(CreateView, self).get_context_data(*args, **kwargs)
        context['account'] = self.account
        return context

    def get_initial(self):
        self.account = None
        if 'slug' in self.kwargs:
            self.account = get_object_or_404(Account, slug=self.kwargs['slug'])
            return {'ledger': self.request.user.ledger, 'show_account': False,
                    'account': self.account}
        else:
            return {'ledger': self.request.user.ledger, 'show_account': True}

    def get_success_message(self, cleaned_data):
        if 'slug' in self.kwargs:
            entries = ', '.join('"#%s"' % e.serial_number for e in self.object)
        else:
            entries = '%s - %s' % (self.object[0].account.name,
                                   ', '.join('"#%s"' % e.serial_number
                                             for e in self.object))
        return self.success_message % {'entries': entries}

    def get_success_url(self):
        if 'slug' in self.kwargs:
            return reverse_lazy('accounts:account_entry_list',
                                args=[self.kwargs['slug']])
        else:
            return reverse_lazy('accounts:entry_list')
