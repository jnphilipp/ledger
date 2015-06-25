from accounts.forms import StandingEntryForm
from accounts.models import Account, Entry
from accounts.templatetags.accounts import floatdot
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

@login_required(login_url='/login/')
@csrf_protect
def add(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
	today = date.today()

	if request.method == 'POST':
		form = StandingEntryForm(request.POST)
		if form.is_valid():
			form.instance.account = account
			entries = form.save()

			messages.add_message(request, messages.SUCCESS, 'the standing entry with numbers %s was successfully created.' % ', '.join(str(entry.serial_number) for entry in entries))
			return redirect('account_entries', slug=account.slug)
		else:
			return render(request, 'ledger/accounts/entry/form.html', locals())
	else:
		form = StandingEntryForm()
		for field in form:
			print(field.label)
		return render(request, 'ledger/accounts/entry/form.html', locals())