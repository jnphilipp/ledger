from accounts.forms import EntryForm
from accounts.models import Account, Entry
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def add(request, slug):
	account = get_object_or_404(Account, slug=slug)
	page = request.GET.get('page')

	if request.method == 'POST':
		form = EntryForm(request.POST)
		if form.is_valid():
			form.instance.account = account
			entry = form.save()

			response = redirect('account_entries', slug=account.slug)
			if page: response['Location'] += '?page=%s' % page
			return response
		else:
			return render(request, 'ledger/accounts/entry/form.html', locals())
	else:
		form = EntryForm()
		return render(request, 'ledger/accounts/entry/form.html', locals())

@csrf_protect
def change(request, slug, entry_id):
	account = get_object_or_404(Account, slug=slug)
	entry = get_object_or_404(Entry, id=entry_id)
	page = request.GET.get('page')

	if request.method == 'POST':
		form = EntryForm(instance=entry, data=request.POST)
		if form.is_valid():
			form.instance.account = account
			entry = form.save()

			response = redirect('account_entries', slug=account.slug)
			if page: response['Location'] += '?page=%s' % page
			return response
		else:
			return render(request, 'ledger/accounts/entry/form.html', locals())
	else:
		form = EntryForm(instance=entry)
		return render(request, 'ledger/accounts/entry/form.html', locals())


@csrf_protect
def swap(request, slug):
	account = get_object_or_404(Account, slug=slug)
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

		response = redirect('account_entries', slug=account.slug)
		if page: response['Location'] += '?page=%s' % page
		return response
	else:
		return redirect('account_entries', slug=account.slug)