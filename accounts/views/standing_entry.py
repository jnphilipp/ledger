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

    def get_initial(self):
        initial = {'ledger': self.request.user.ledger}
        if 'slug' in self.kwargs:
            initial['account'] = get_object_or_404(Account,
                                                   slug=self.kwargs['slug'])
        return initial

    def get_success_message(self, cleaned_data):
        entries = f'{self.object[0].account.name} - ' + \
            f'#{", #".join(str(e.serial_number) for e in self.object)}'
        return self.success_message % {'entries': entries}

    def get_success_url(self):
        url = reverse_lazy('create_another_success')
        if 'reload' in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        return url
