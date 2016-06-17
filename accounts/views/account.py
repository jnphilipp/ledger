# -*- coding: utf-8 -*-

from accounts.forms import AccountForm
from accounts.models import Account
from categories.models import Category, Tag
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from ledger.functions.dates import get_last_date_current_month
from users.models import Ledger


@login_required(login_url='/users/signin/')
def accounts(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    accounts = Account.objects.filter(ledger=ledger)
    return render(request, 'accounts/account/accounts.html', locals())


@login_required(login_url='/users/signin/')
def account(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    entries = account.entries.filter(day__lte=get_last_date_current_month()).reverse()[:5]
    return render(request, 'accounts/account/account.html', locals())


@login_required(login_url='/users/signin/')
def statistics(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    chart = request.GET.get('chart')
    year = request.GET.get('year')
    month = request.GET.get('month')
    category = get_object_or_404(Category, slug=request.GET.get('category')) if request.GET.get('category') else None
    tag = get_object_or_404(Tag, slug=request.GET.get('tag')) if request.GET.get('tag') else None
    
    if year and month:
        month_name = date(year=int(year), month=int(month), day=1).strftime('%B').lower()

    options = []
    if not chart:
        option_name = 'chart'
        options = [{'id':'categories', 'key':'chart', 'value':'categories'}, {'id':'tags', 'key':'chart', 'value':'tags'}]
    elif chart and not year:
        years = account.entries.dates('day', 'year')
        if chart == 'tags':
            years = years.filter(tags__isnull=False)

        option_name = 'year'
        options = [{'id':year.strftime('%Y'), 'key':'year', 'value':year.strftime('%Y')} for year in years]
    elif chart and year and not month:
        months = account.entries.filter(day__year=year).dates('day', 'month')
        if chart == 'tags':
            months = months.filter(tags__isnull=False)

        option_name = 'month'
        options = [{'id':month.strftime('%m'), 'key':'month', 'value':month.strftime('%B').lower()} for month in months]
    elif chart and year and month and not category and not tag:
        if chart == 'categories':
            option_name = 'category'
            options = [{'id':category.slug, 'key':'category', 'value':category.name.lower()} for category in Category.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
        elif chart == 'tags':
            option_name = 'tag'
            options = [{'id':tag.slug, 'key':'tag', 'value':tag.name.lower()} for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
    return render(request, 'accounts/account/statistics.html', locals())


@login_required(login_url='/users/signin/')
@csrf_protect
def add(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    if request.method == 'POST':
        form = AccountForm(ledger, data=request.POST)
        if form.is_valid():
            account = form.save()
            ledger = get_object_or_404(Ledger, user=request.user)
            ledger.accounts.add(account)
            ledger.save()
            messages.add_message(request, messages.SUCCESS, _('the account %(name)s was successfully created.' % {'name': account.name.lower()}))
            return redirect('account', slug=account.slug)
        return render(request, 'accounts/account/form.html', locals())
    else:
        form = AccountForm(ledger)
    return render(request, 'accounts/account/form.html', locals())


@login_required(login_url='/users/signin/')
@csrf_protect
def edit(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    if request.method == 'POST':
        form = AccountForm(ledger, instance=account, data=request.POST)
        if form.is_valid():
            account = form.save()
            messages.add_message(request, messages.SUCCESS, _('the account %(name)s was successfully updated.') % {'name': account.name.lower()})
            return redirect('account', slug=account.slug)
        return render(request, 'accounts/account/form.html', locals())
    else:
        form = AccountForm(ledger, instance=account)
    return render(request, 'accounts/account/form.html', locals())


@login_required(login_url='/users/signin/')
@csrf_protect
def delete(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    if request.method == 'POST':
        account.delete()
        messages.add_message(request, messages.SUCCESS, _('the account %(name)s was successfully deleted.') % {'name': account.name.lower()})
        return redirect('dashboard')
    return render(request, 'accounts/account/delete.html', locals())
