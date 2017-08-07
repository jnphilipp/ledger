# -*- coding: utf-8 -*-

from accounts.forms import EntryForm, EntryFilterForm
from accounts.models import Account, Entry
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from ledger.functions.dates import get_last_date_current_month
from users.models import Ledger


@login_required
@csrf_protect
def list(request, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None

    if request.method == 'POST':
        form = EntryFilterForm(request.POST)
        if account:
            del form.fields['accounts']
            del form.fields['units']
            entry_list = account.entries.all().reverse()
        else:
            entry_list = Entry.objects.filter(account__ledger=ledger)
        if form.is_valid():
            if form.cleaned_data['start_date']:
                entry_list = entry_list.filter(day__gte=form.cleaned_data['start_date'])
            if form.cleaned_data['end_date']:
                entry_list = entry_list.filter(day__lte=form.cleaned_data['end_date'])
            if 'accounts' in form.cleaned_data and form.cleaned_data['accounts']:
                entry_list = entry_list.filter(account__in=form.cleaned_data['accounts'])
            if form.cleaned_data['categories']:
                entry_list = entry_list.filter(category__in=form.cleaned_data['categories'])
            if form.cleaned_data['tags']:
                entry_list = entry_list.filter(tags__in=form.cleaned_data['tags'])
            if 'units' in form.cleaned_data and form.cleaned_data['units']:
                entry_list = entry_list.filter(account__unit__in=form.cleaned_data['units'])
        if not account:
            entry_list = entry_list.order_by('-day', '-id')
    else:
        form = EntryFilterForm()
        if account:
            del form.fields['accounts']
            del form.fields['units']
            entry_list = account.entries.filter(day__lte=get_last_date_current_month()).reverse()
        else:
            entry_list = Entry.objects.filter(account__ledger=ledger).filter(day__lte=get_last_date_current_month()).order_by('-day', '-id')

    show_options = not account.closed if account else True
    paginator = Paginator(entry_list, 200)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    content_type = ContentType.objects.get_for_model(Entry)
    return render(request, 'accounts/entry/list.html', locals())


@login_required
@csrf_protect
def detail(request, entry_id, slug=None):
    o = request.GET.get('o') if not request.GET.get('o') == None else 'name'
    order = o if o else 'name'

    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None
    entry = get_object_or_404(Entry, id=entry_id)
    files = entry.files.all().order_by(order)
    content_type = ContentType.objects.get_for_model(Entry)
    return render(request, 'accounts/entry/detail.html', locals())


@login_required
@csrf_protect
def add(request, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None
    page = request.GET.get('page')
    today = date.today()

    if request.method == 'POST':
        form = EntryForm(ledger, data=request.POST, exclude_account=bool(account))
        if form.is_valid():
            if account:
                form.instance.account = account
            entry = form.save()

            messages.add_message(request, messages.SUCCESS, _('The entry "%(entry)s" was successfully created.') % {'entry': '#%s' % entry.serial_number if account else '%s - #%s' % (entry.account.name, entry.serial_number)})
            response = redirect('accounts:account_entries', slug=account.slug) if account else redirect('accounts:entries')
            if page: response['Location'] += '?page=%s' % page
            return response
        return render(request, 'accounts/entry/form.html', locals())
    else:
        form = EntryForm(ledger, exclude_account=bool(account))
    return render(request, 'accounts/entry/form.html', locals())


@login_required
@csrf_protect
def edit(request, entry_id, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None
    entry = get_object_or_404(Entry, id=entry_id)
    page = request.GET.get('page')
    today = date.today()

    if request.method == 'POST':
        form = EntryForm(ledger, instance=entry, data=request.POST, exclude_account=bool(account))
        if form.is_valid():
            no = entry.serial_number
            if account:
                form.instance.account = account
            entry = form.save()


            if no == entry.serial_number:
                msg = _('The entry "%(entry)s" was successfully updated.') % {'entry': '#%s' % no if account else '%s - #%s'% (entry.account.name, no)}
            else:
                msg = _('The entry "%(entry)s" was successfully updated and moved to "%(no)s".') % {'entry': '#%s' % no if account else '%s - #%s'% (entry.account.name, no), 'no': '#%s' % entry.serial_number if account else '%s - #%s'% (entry.account.name, entry.serial_number)}
            messages.add_message(request, messages.SUCCESS, msg)
            response = redirect('accounts:account_entries', slug=account.slug) if account else redirect('accounts:entries')
            if page:
                response['Location'] += '?page=%s' % page
            return response
        return render(request, 'accounts/entry/form.html', locals())
    else:
        form = EntryForm(ledger, instance=entry, exclude_account=bool(account))
    return render(request, 'accounts/entry/form.html', locals())


@login_required
@csrf_protect
def delete(request, entry_id, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None
    entry = get_object_or_404(Entry, id=entry_id)
    if request.method == 'POST':
        entry.delete()
        messages.add_message(request, messages.SUCCESS, _('The entry "%(entry)s" was successfully deleted.') % {'entry': '#%s' % entry.serial_number if account else '%s - #%s' % (entry.account.name, entry.serial_number)})
        for entry in Entry.objects.filter(account=entry.account).filter(serial_number__gt=entry.serial_number):
            entry.serial_number -= 1
            entry.save()
        entry.account.save()
        return redirect('accounts:account_entries', slug=account.slug) if account else redirect('accounts:entries')
    return render(request, 'accounts/entry/delete.html', locals())


@login_required
def duplicate(request, entry_id, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger) if slug else None
    entry = get_object_or_404(Entry, id=entry_id)

    new = Entry.objects.create(account=account if account else entry.account, day=date.today(), amount=entry.amount, category=entry.category, additional=entry.additional)
    for tag in entry.tags.all():
        new.tags.add(tag.id)
    new.save()
    messages.add_message(request, messages.SUCCESS, _('The entry "%(old_entry)s" has been successfully duplicated as entry "%(new_entry)s".') % {'old_entry': '#%s' % entry.serial_number if account else '%s - #%s' % (entry.account.name, entry.serial_number), 'new_entry': '#%s' % new.serial_number if account else '%s - #%s' % (new.account.name, new.serial_number)})
    return redirect('accounts:account_entries', slug=account.slug) if account else redirect('accounts:entries')


@login_required
@csrf_protect
def swap(request, slug, e1, e2):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    page = request.GET.get('page')

    e1 = get_object_or_404(Entry, id=e1)
    e2 = get_object_or_404(Entry, id=e2)

    tmp = e1.serial_number
    e1.serial_number = e2.serial_number
    e2.serial_number = -1
    e2.save()
    e1.save()

    e2.serial_number = tmp
    e2.save()

    messages.add_message(request, messages.SUCCESS, _('The entries "#%(e1)s" and "#%(e2)s" were successfully swaped.') % {'e1': e2.serial_number, 'e2': e1.serial_number})
    response = redirect('accounts:account_entries', slug=account.slug)
    if page: response['Location'] += '?page=%s' % page
    return response
