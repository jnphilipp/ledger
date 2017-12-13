# -*- coding: utf-8 -*-

from accounts.forms import StandingEntryForm
from accounts.models import Account
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from users.models import Ledger


@login_required
@csrf_protect
def add(request, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None
    today = date.today()

    if request.method == 'POST':
        form = StandingEntryForm(ledger, data=request.POST,
                                 exclude_account=bool(account))
        if form.is_valid():
            if account:
                form.instance.account = account
            entries = form.save()

            msg = _('The standing entry with the entries %(entries)s was ' +
                    'successfully created.')
            if account:
                entries = ', '.join('"#%s"' % e.serial_number for e in entries)
            else:
                entries = '%s - %s' % (
                    entries[0].account.name,
                    ', '.join('"#%s"' % e.serial_number for e in entries)
                )

            messages.add_message(request, messages.SUCCESS,
                                 msg % {'entries': entries})

            if account:
                return redirect('accounts:account_entries', slug=account.slug)
            else:
                return redirect('accounts:entries')
        return render(request, 'accounts/entry/form.html', locals())
    else:
        form = StandingEntryForm(ledger, exclude_account=bool(account))
    return render(request, 'accounts/entry/form.html', locals())
