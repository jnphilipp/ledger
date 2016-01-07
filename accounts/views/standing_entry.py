# -*- coding: utf-8 -*-

from accounts.forms import StandingEntryForm
from accounts.models import Account, Entry
from accounts.templatetags.accounts import floatdot
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

@login_required(login_url='/profile/signin/')
@csrf_protect
def add(request, slug=None):
    account = get_object_or_404(Account, slug=slug, ledger__user=request.user) if slug else None
    today = date.today()

    if request.method == 'POST':
        form = StandingEntryForm(data=request.POST, exclude_account=True if account else False)
        if form.is_valid():
            if account: form.instance.account = account
            entries = form.save()

            messages.add_message(request, messages.SUCCESS, 'the standing entryies "%s%s" were successfully created.' % ('' if account else '%s - ' % entries[0].account, ', '.join('#%s' % entry.serial_number for entry in entries)))
            return redirect('account_entries', slug=account.slug) if account else redirect('entries')
        else:
            return render(request, 'ledger/accounts/entry/form.html', locals())
    else:
        form = StandingEntryForm(exclude_account=True if account else False)
        return render(request, 'ledger/accounts/entry/form.html', locals())
