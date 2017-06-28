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
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from ledger.functions.dates import get_last_date_current_month
from users.models import Ledger


@login_required
def list(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    accounts = Account.objects.filter(ledger=ledger)
    return render(request, 'accounts/account/list.html', locals())


@login_required
def detail(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    entries = account.entries.filter(day__lte=get_last_date_current_month()).reverse()[:5]
    return render(request, 'accounts/account/detail.html', locals())


@login_required
def statistics(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    chart = request.GET.get('chart')
    year = request.GET.get('year')
    month = request.GET.get('month')
    category = get_object_or_404(Category, slug=request.GET.get('category')) if request.GET.get('category') else None
    tag = get_object_or_404(Tag, slug=request.GET.get('tag')) if request.GET.get('tag') else None

    if year and month:
        month_name = date(year=int(year), month=int(month), day=1).strftime('%B')

    options = []
    if not chart:
        option_msg = _('Select a chart')
        options = [{
            'id': 'categories',
            'key': 'chart',
            'value': _('Categories')
        },
        {
            'id': 'tags',
            'key': 'chart',
            'value': _('Tags')
        }]
    elif chart and not year:
        years = account.entries.dates('day', 'year')
        if chart == 'tags':
            chart_name = _('Tags')
            years = years.filter(tags__isnull=False)
        else:
            chart_name = _('Categories')

        option_msg = _('Select a year')
        option_name = 'year'
        options = [{
            'id': year.strftime('%Y'),
            'key': 'year',
            'value': year.strftime('%Y')
        } for year in years]
    elif chart and year and not month:
        months = account.entries.filter(day__year=year).dates('day', 'month')
        if chart == 'tags':
            chart_name = _('Tags')
            months = months.filter(tags__isnull=False)
        else:
            chart_name = _('Categories')

        option_msg = _('Select a month')
        options = [{
            'id': month.strftime('%m'),
            'key': 'month',
            'value': _(month.strftime('%B'))
        } for month in months]
    elif chart and year and month and not category and not tag:
        if chart == 'categories':
            chart_name = _('Categories')
            option_msg = _('Select a category')
            options = [{
                'id': category.slug,
                'key': 'category',
                'value': category.name
            } for category in Category.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
        elif chart == 'tags':
            chart_name = _('Tags')
            option_msg = _('Select a tag')
            options = [{
                'id': tag.slug,
                'key': 'tag',
                'value': tag.name
            } for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
    else:
        chart_name = _('Tags') if chart == 'tags' else _('Categories')
    return render(request, 'accounts/account/statistics.html', locals())


@login_required
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
            messages.add_message(request, messages.SUCCESS, _('The account %(name)s was successfully created.' % {'name': account.name}))
            return redirect('accounts:account', slug=account.slug)
        return render(request, 'accounts/account/form.html', locals())
    else:
        form = AccountForm(ledger)
    return render(request, 'accounts/account/form.html', locals())


@login_required
@csrf_protect
def edit(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    if request.method == 'POST':
        form = AccountForm(ledger, instance=account, data=request.POST)
        if form.is_valid():
            account = form.save()
            messages.add_message(request, messages.SUCCESS, _('The account %(name)s was successfully updated.') % {'name': account.name})
            return redirect('accounts:account', slug=account.slug)
        return render(request, 'accounts/account/form.html', locals())
    else:
        form = AccountForm(ledger, instance=account)
    return render(request, 'accounts/account/form.html', locals())


@login_required
def close(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    account.closed = not account.closed
    account.save()
    if account.closed:
        messages.add_message(request, messages.SUCCESS, _('The account %(name)s was successfully closed.') % {'name': account.name})
    else:
        messages.add_message(request, messages.SUCCESS, _('The account %(name)s was successfully re-open.') % {'name': account.name})
    return redirect('accounts:account', slug=account.slug)


@login_required
@csrf_protect
def delete(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    if request.method == 'POST':
        account.delete()
        messages.add_message(request, messages.SUCCESS, _('The account %(name)s was successfully deleted.') % {'name': account.name})
        return redirect('dashboard')
    return render(request, 'accounts/account/delete.html', locals())
