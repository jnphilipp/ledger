from accounts.charts import account_chart
from accounts.functions.dates import get_last_date_current_month
from accounts.forms import AccountForm, FilterForm
from accounts.models import Account, Category, Entry, Tag, Unit
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

@login_required(login_url='/login/')
def account(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
	entries = account.entry_set.filter(day__lt=get_last_date_current_month()).reverse()[:5]

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

	account_categories_chart_data, categories_chart_library = account_chart('categories', account)
	account_tags_chart_data, tags_chart_library = account_chart('tags', account)

	return render(request, 'ledger/accounts/account/account.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def entries(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)

	if request.method == 'POST':
		form = FilterForm(request.POST)
		entries = account.entry_set.all().reverse()
		if form.is_valid():
			if form.cleaned_data['categories']:
				entries = entries.filter(category__in=form.cleaned_data['categories'])
			if form.cleaned_data['tags']:
				entries = entries.filter(tags__in=form.cleaned_data['tags'])
	else:
		form = FilterForm()
		entries = account.entry_set.filter(day__lt=get_last_date_current_month()).reverse()
	return render(request, 'ledger/accounts/account/entries.html', locals())

@login_required(login_url='/login/')
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

	if not chart:
		option_name = 'chart'
		options = [{'id':'categories', 'key':'chart', 'value':'categories'}, {'id':'tags', 'key':'chart', 'value':'tags'}]
	elif chart and not year:
		years = account.entry_set.dates('day', 'year')
		if chart == 'tags':
			years = years.filter(tags__isnull=False)

		option_name = 'year'
		options = [{'id':year.strftime('%Y'), 'key':'year', 'value':year.strftime('%Y')} for year in years]
		data, library = account_chart(chart, account)
	elif chart and year and not month:
		months = account.entry_set.filter(day__year=year).dates('day', 'month')
		if chart == 'tags':
			months = months.filter(tags__isnull=False)

		option_name = 'month'
		options = [{'id':month.strftime('%m'), 'key':'month', 'value':month.strftime('%B').lower()} for month in months]
		data, library = account_chart(chart, account, year=year)
	elif chart and year and month and not category and not tag:
		data, library = account_chart(chart, account, year=year, month=month)

		if chart == 'categories':
			option_name = 'category'
			options = [{'id':category.slug, 'key':'category', 'value':category.name.lower()} for category in Category.objects.filter(Q(entry__account=account) & Q(entry__day__year=year) & Q(entry__day__month=month)).distinct()]
			print(options)
		elif chart == 'tags':
			option_name = 'tag'
			options = [{'id':tag.slug, 'key':'tag', 'value':tag.name.lower()} for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
		else:
			options = []
	elif chart and year and month and category:
		data, library = account_chart(chart, account, year=year, month=month, category=category)
		options = []
	elif chart and year and month and tag:
		data, library = account_chart(chart, account, year=year, month=month, tag=tag)
		options = []
	else:
		options = []

	return render(request, 'ledger/accounts/account/statistics.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def add(request):
	if request.method == 'POST':
		form = AccountForm(request.POST)
		if form.is_valid():
			account = form.save()
			ledger = get_object_or_404(Ledger, user=request.user)
			ledger.accounts.add(account)
			ledger.save()
			messages.add_message(request, messages.SUCCESS, 'the account %s was successfully created.' % account.name.lower())
			return redirect('account', slug=account.slug)
		else:
			return render(request, 'ledger/accounts/account/form.html', locals())
	else:
		form = AccountForm()
		return render(request, 'ledger/accounts/account/form.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def edit(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
	if request.method == 'POST':
		form = AccountForm(instance=account, data=request.POST)
		if form.is_valid():
			account = form.save()
			messages.add_message(request, messages.SUCCESS, 'the account %s was successfully updated.' % account.name.lower())
			return redirect('account', slug=account.slug)
		else:
			return render(request, 'ledger/accounts/account/form.html', locals())
	else:
		form = AccountForm(instance=account)
		return render(request, 'ledger/accounts/account/form.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def delete(request, slug):
	account = get_object_or_404(Account, slug=slug, ledger__user=request.user)
	if request.method == 'POST':
		account.delete()
		messages.add_message(request, messages.SUCCESS, 'the account %s was successfully deleted.' % account.name.lower())
		return redirect('dashboard')
	return render(request, 'ledger/accounts/account/delete.html', locals())