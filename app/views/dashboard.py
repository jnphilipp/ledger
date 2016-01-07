# -*- coding: utf-8 -*-

from accounts.functions.dates import get_last_date_current_month
from accounts.models import Account, Entry, Unit
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/profile/signin/')
def dashboard(request):
    accounts = Account.objects.filter(ledger__user=request.user)
    units = Unit.objects.filter(account__in=accounts).distinct()
    entries = Entry.objects.filter(account__ledger__user=request.user).filter(day__lte=get_last_date_current_month()).order_by('-day', '-id')[:10]
    return render(request, 'ledger/dashboard/dashboard.html', locals())
