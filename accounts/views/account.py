from accounts.charts import account_chart
from accounts.forms import AccountForm
from accounts.models import Category, Entry, Account, Unit
from app.models import Ledger
from collections import OrderedDict
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Count, Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

@login_required(login_url='/login/')
def dashboard(request):
	accounts = Account.objects.filter(ledger__user=request.user)
	return render(request, 'ledger/accounts/dashboard/dashboard.html', locals())

def account(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
	entries = account.entry_set.all().reverse()[:5]

	cs = Entry.objects.filter(account=account).values('category__name').annotate(count=Count('category')).order_by('category__name')
	categories = {}
	for c in cs:
		categories[c['category__name'].lower() if len(c['category__name']) <= 15 else '%s…' % c['category__name'][0:13].lower()] = c['count']
	if categories:
		category_data = [{'data':OrderedDict(sorted(categories.items())), 'name':'entries'}]

	ts = Entry.objects.filter(account=account).filter(tags__isnull=False).values('tags__name').annotate(count=Count('tags')).order_by('tags__name')
	tags = {}
	for t in ts:
		tags[t['tags__name'].lower()] = t['count']
	if tags:
		tag_data = [{'data':OrderedDict(sorted(tags.items())), 'name':'entries'}]

	account_chart_data, library = account_chart(account)

	return render(request, 'ledger/accounts/account/account.html', locals())

def entries(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
	entries = account.entry_set.all().reverse()
	return render(request, 'ledger/accounts/account/entries.html', locals())

def statistics(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
	year = request.GET.get('year')
	month = request.GET.get('month')
	category = get_object_or_404(Category, slug=request.GET.get('category')) if request.GET.get('category') else None
	if year and month:
		month_name = date(year=int(year), month=int(month), day=1).strftime('%B').lower()

	cs = Entry.objects.filter(account=account).values('category__name').annotate(count=Count('category')).order_by('category__name')
	categories = {}
	for c in cs:
		categories[c['category__name'].lower() if len(c['category__name']) <= 15 else '%s…' % c['category__name'][0:13].lower()] = c['count']
	category_data = [{'data':OrderedDict(sorted(categories.items())), 'name':'entries'}]

	ts = Entry.objects.filter(account=account).filter(tags__isnull=False).values('tags__name').annotate(count=Count('tags')).order_by('tags__name')
	tags = {}
	for t in ts:
		tags[t['tags__name'].lower()] = t['count']
	tag_data = [{'data':OrderedDict(sorted(tags.items())), 'name':'entries'}]

	data, library = account_chart(account, year=year, month=month, category=category)
	years = account.entry_set.dates('day', 'year')
	if year:
		months = account.entry_set.filter(day__year=year).dates('day', 'month')
		if month:
			categories = Category.objects.filter(id__in=account.entry_set.filter(day__year=year).filter(day__month=month).values_list('category', flat=True))

	return render(request, 'ledger/accounts/account/statistics.html', locals())

@csrf_protect
def add_account(request):
	if request.method == 'POST':
		form = AccountForm(request.POST)
		if form.is_valid():
			unit = form.cleaned_data['unit']
			account = Account.objects.create(name=form.cleaned_data['name'], unit=unit)
			ledger = get_object_or_404(Ledger, user=request.user)
			ledger.accounts.add(account)
			messages.add_message(request, messages.SUCCESS, 'the account %s was successfully created.' % account.name)
			return redirect('account', slug=account.slug)
		else:
			return render(request, 'ledger/accounts/account/add.html', locals())
	else:
		form = AccountForm()
		return render(request, 'ledger/accounts/account/add.html', locals())