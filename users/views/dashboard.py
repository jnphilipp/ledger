# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ledger.functions.dates import get_last_date_current_month
from units.models import Unit


@login_required
def dashboard(request):
    accounts = Account.objects.filter(ledger__user=request.user)
    units = Unit.objects.filter(accounts__in=accounts).distinct()
    entries = Entry.objects.filter(account__ledger__user=request.user).filter(day__lte=get_last_date_current_month()).order_by('-day', '-id')[:10]
    return render(request, 'users/dashboard.html', locals())
