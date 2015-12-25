# -*- coding: utf-8 -*-

from accounts.forms import EntryForm
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
def add(request, slug):
    account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
    page = request.GET.get('page')
    today = date.today()

    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            form.instance.account = account
            entry = form.save()

            messages.add_message(request, messages.SUCCESS, 'the entry number %s was successfully created.' % entry.serial_number)
            response = redirect('account_entries', slug=account.slug)
            if page: response['Location'] += '?page=%s' % page
            return response
        else:
            return render(request, 'ledger/accounts/entry/form.html', locals())
    else:
        form = EntryForm()
        return render(request, 'ledger/accounts/entry/form.html', locals())

@login_required(login_url='/profile/signin/')
@csrf_protect
def edit(request, slug, entry_id):
    account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
    entry = get_object_or_404(Entry, id=entry_id)
    page = request.GET.get('page')
    today = date.today()

    if request.method == 'POST':
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            no = entry.serial_number
            form.instance.account = account
            entry = form.save()

            if no == entry.serial_number:
                messages.add_message(request, messages.SUCCESS, 'entry "%s" was successfully updated.' % entry.serial_number)
            else:
                messages.add_message(request, messages.SUCCESS, 'entry "%s" was successfully updated and moved to "%s".' % (no, entry.serial_number))
            response = redirect('account_entries', slug=account.slug)
            if page: response['Location'] += '?page=%s' % page
            return response
        else:
            return render(request, 'ledger/accounts/entry/form.html', locals())
    else:
        form = EntryForm(instance=entry)
        return render(request, 'ledger/accounts/entry/form.html', locals())

@login_required(login_url='/profile/signin/')
@csrf_protect
def delete(request, slug, entry_id):
    account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
    entry = get_object_or_404(Entry, id=entry_id)
    if request.method == 'POST':
        entry.delete()
        messages.add_message(request, messages.SUCCESS, 'the entry number %s was successfully deleted.' % entry.serial_number)
        for entry in Entry.objects.filter(account=account).filter(serial_number__gt=entry.serial_number):
            entry.serial_number -= 1
            entry.save()
        account.save()
        return redirect('account_entries', slug=account.slug)
    return render(request, 'ledger/accounts/entry/delete.html', locals())

@login_required(login_url='/profile/signin/')
def duplicate(request, slug, entry_id):
    account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
    entry = get_object_or_404(Entry, id=entry_id)

    new = Entry.objects.create(account=account, day=date.today(), amount=entry.amount, category=entry.category, additional=entry.additional)
    for tag in entry.tags.all():
        new.tags.add(tag.id)
    new.save()
    messages.add_message(request, messages.SUCCESS, 'the entry number %s has been successfully duplicated as entry number %s.' % (entry.serial_number, new.serial_number))
    return redirect('account_entries', slug=account.slug)

@login_required(login_url='/profile/signin/')
@csrf_protect
def swap(request, slug):
    account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
    page = request.GET.get('page')

    if request.method == 'POST':
        e1 = get_object_or_404(Entry, id=request.POST.get('e1', ''))
        e2 = get_object_or_404(Entry, id=request.POST.get('e2', ''))

        tmp = e1.serial_number
        e1.serial_number = e2.serial_number
        e2.serial_number = -1
        e2.save()
        e1.save()

        e2.serial_number = tmp
        e2.save()

        messages.add_message(request, messages.SUCCESS, 'the entries %s and %s were successfully swaped.' % (e2.serial_number, e1.serial_number))
        response = redirect('account_entries', slug=account.slug)
        if page: response['Location'] += '?page=%s' % page
        return response
    else:
        return redirect('account_entries', slug=account.slug)
