# -*- coding: utf-8 -*-

from accounts.forms import StandingEntryForm
from accounts.models import Account
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from users.models import Ledger


@login_required(login_url='/profile/signin/')
@csrf_protect
def add(request, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None
    today = date.today()

    if request.method == 'POST':
        form = StandingEntryForm(ledger, data=request.POST, exclude_account=bool(account))
        if form.is_valid():
            if account:
                form.instance.account = account
            entries = form.save()

            messages.add_message(request, messages.SUCCESS, _('the standing entry with the entries %(entries)s was successfully created.') % {'entries': ', '.join('"#%s"' % entry.serial_number for entry in entries) if account else '%s - %s' % (entries[0].account.name.lower(), ', '.join('"#%s"' % entry.serial_number for entry in entries))})
            return redirect('account_entries', slug=account.slug) if account else redirect('entries')
        return render(request, 'accounts/entry/form.html', locals())
    else:
        form = StandingEntryForm(ledger, exclude_account=bool(account))
    return render(request, 'accounts/entry/form.html', locals())
