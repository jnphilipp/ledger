# -*- coding: utf-8 -*-

from accounts.forms import EntryForm, EntryFilterForm
from accounts.models import Account, Entry
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from ledger.functions.dates import get_last_date_current_month
from users.models import Ledger


@method_decorator(login_required, name='dispatch')
class ListView(generic.ListView):
    context_object_name = 'entries'
    model = Entry
    paginate_by = 200

    def get_queryset(self):
        self.form = EntryFilterForm(self.request.GET)
        if 'slug' in self.kwargs:
            del self.form.fields['accounts']
            del self.form.fields['units']
            entries = Entry.objects. \
                filter(account__ledger__user=self.request.user). \
                filter(account__slug=self.kwargs['slug']). \
                order_by('-serial_number')
        else:
            entries = Entry.objects. \
                filter(account__ledger__user=self.request.user). \
                order_by('-day', '-id')

        filtered = False
        self.start_date = None
        self.end_date = None
        self.accounts = []
        self.categories = []
        self.tags = []
        self.units = []
        if self.form.is_valid():
            if self.form.cleaned_data['start_date']:
                filtered = True
                self.start_date = self.form.cleaned_data['start_date']
                entries = entries.filter(day__gte=self.start_date)
            if self.form.cleaned_data['end_date']:
                filtered = True
                self.end_date = self.form.cleaned_data['end_date']
                entries = entries.filter(day__lte=self.end_date)
            if 'accounts' in self.form.cleaned_data and \
                    self.form.cleaned_data['accounts']:
                filtered = True
                self.accounts = [a.pk for a in
                                 self.form.cleaned_data['accounts']]
                entries = entries.filter(account__in=self.accounts)
            if self.form.cleaned_data['categories']:
                filtered = True
                self.categories = [c.pk for c in
                                   self.form.cleaned_data['categories']]
                entries = entries.filter(category__in=self.categories)
            if self.form.cleaned_data['tags']:
                filtered = True
                self.tags = [t.pk for t in self.form.cleaned_data['tags']]
                entries = entries.filter(tags__in=self.tags)
            if 'units' in self.form.cleaned_data and \
                    self.form.cleaned_data['units']:
                filtered = True
                self.units = [u.pk for u in self.form.cleaned_data['units']]
                entries = entries.filter(account__unit__in=self.units)

        if not filtered:
            entries = entries.filter(day__lte=get_last_date_current_month())

        return entries.distinct()

    def get_context_data(self, *args, **kwargs):
        context = super(ListView, self).get_context_data(*args, **kwargs)

        context['form'] = self.form
        context['start_date'] = self.start_date
        context['end_date'] = self.end_date
        context['accounts'] = self.accounts
        context['categories'] = self.categories
        context['tags'] = self.tags
        context['units'] = self.units
        if 'slug' in self.kwargs:
            context['account'] = context['entries'][0].account
            context['show_options'] = not context['account'].closed
        else:
            context['show_options'] = True
        return context


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Entry

    def get_object(self, queryset=None):
        if 'slug' in self.kwargs and self.kwargs['slug']:
            return Entry.objects.get(account__slug=self.kwargs['slug'],
                                     pk=self.kwargs['pk'])
        else:
            return Entry.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context['content_type'] = ContentType.objects.get_for_model(Entry)
        context['o'] = 'name'
        if 'o' in self.request.GET:
            context['o'] = self.request.GET.get('o')
        context['files'] = context['entry'].files.all().order_by(context['o'])
        if 'slug' in self.kwargs:
            context['account'] = context['entry'].account
        return context


@login_required
@csrf_protect
def add(request, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug,
                                ledger=ledger) if slug else None
    today = date.today()

    if request.method == 'POST':
        form = EntryForm(ledger, data=request.POST,
                         exclude_account=bool(account))
        if form.is_valid():
            if account:
                form.instance.account = account
            entry = form.save()

            msg = _('The entry "%(entry)s" was successfully created.') % {
                'entry': '#%s' % entry.serial_number if account
                else '%s - #%s' % (entry.account.name, entry.serial_number)}
            messages.add_message(request, messages.SUCCESS, msg)

            if account:
                return redirect('accounts:account_entry_list',
                                slug=account.slug)
            else:
                return redirect('accounts:entry_list')
        return render(request, 'accounts/entry/form.html', locals())
    else:
        form = EntryForm(ledger, exclude_account=bool(account))
    return render(request, 'accounts/entry/form.html', locals())


@login_required
@csrf_protect
def edit(request, entry_id, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug,
                                ledger=ledger) if slug else None
    entry = get_object_or_404(Entry, id=entry_id)
    today = date.today()

    if request.method == 'POST':
        form = EntryForm(ledger, instance=entry, data=request.POST,
                         exclude_account=bool(account))
        if form.is_valid():
            no = entry.serial_number
            if account:
                form.instance.account = account
            entry = form.save()

            if no == entry.serial_number:
                msg = _('The entry "%(entry)s" was successfully updated.') % {
                    'entry': '#%s' % no if account
                    else '%s - #%s' % (entry.account.name, no)}
            else:
                msg = _('The entry "%(entry)s" was successfully updated and' +
                        ' moved to "%(no)s".') % {
                    'entry': '#%s' % no if account else
                    '%s - #%s' % (entry.account.name, no),
                    'no': '#%s' % entry.serial_number if account else
                    '%s - #%s' % (entry.account.name, entry.serial_number)}
            messages.add_message(request, messages.SUCCESS, msg)

            if account:
                return redirect('accounts:account_entry_list',
                                slug=account.slug)
            else:
                return redirect('accounts:entry_list')
        return render(request, 'accounts/entry/form.html', locals())
    else:
        form = EntryForm(ledger, instance=entry, exclude_account=bool(account))
    return render(request, 'accounts/entry/form.html', locals())


@login_required
@csrf_protect
def delete(request, entry_id, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug,
                                ledger=ledger) if slug else None
    entry = get_object_or_404(Entry, id=entry_id)
    if request.method == 'POST':
        entry.delete()
        msg = _('The entry "%(entry)s" was successfully deleted.') % {
            'entry': '#%s' % entry.serial_number if account
            else '%s - #%s' % (entry.account.name, entry.serial_number)}
        messages.add_message(request, messages.SUCCESS, msg)
        for entry in Entry.objects.filter(account=entry.account). \
                filter(serial_number__gt=entry.serial_number):
            entry.serial_number -= 1
            entry.save()
        entry.account.save()
        if account:
            return redirect('accounts:account_entry_list', slug=account.slug)
        else:
            return redirect('accounts:entry_list')
    return render(request, 'accounts/entry/delete.html', locals())


@login_required
def duplicate(request, entry_id, slug=None):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug,
                                ledger=ledger) if slug else None
    entry = get_object_or_404(Entry, id=entry_id)

    new = Entry.objects.create(account=account if account
                               else entry.account, day=date.today(),
                               amount=entry.amount, category=entry.category,
                               additional=entry.additional)
    for tag in entry.tags.all():
        new.tags.add(tag.id)
    new.save()
    msg = _('The entry "%(old_entry)s" has been successfully duplicated as ' +
            'entry "%(new_entry)s".') % {
        'old_entry': '#%s' % entry.serial_number if account
        else '%s - #%s' % (entry.account.name, entry.serial_number),
        'new_entry': '#%s' % new.serial_number if account
        else '%s - #%s' % (new.account.name, new.serial_number)}
    messages.add_message(request, messages.SUCCESS, msg)
    if account:
        return redirect('accounts:account_entry_list', slug=account.slug)
    else:
        return redirect('accounts:entry_list')


@login_required
@csrf_protect
def swap(request, slug, e1, e2):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)

    e1 = get_object_or_404(Entry, id=e1)
    e2 = get_object_or_404(Entry, id=e2)

    tmp = e1.serial_number
    e1.serial_number = e2.serial_number
    e2.serial_number = -1
    e2.save()
    e1.save()

    e2.serial_number = tmp
    e2.save()

    msg = _('The entries "#%(e1)s" and "#%(e2)s" were successfully ' +
            'swaped.') % {'e1': e2.serial_number, 'e2': e1.serial_number}
    messages.add_message(request, messages.SUCCESS, msg)
    return redirect('accounts:account_entry_list', slug=account.slug)
