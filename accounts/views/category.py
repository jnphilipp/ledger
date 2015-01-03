from accounts.models import Category
from collections import OrderedDict
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

def categories(request):
	paginator = Paginator(Category.objects.all(), 28)
	page = request.GET.get('page')
	try:
		categories = paginator.page(page)
		page = int(page)
	except PageNotAnInteger:
		page = 1
		categories = paginator.page(1)
	except EmptyPage:
		page = paginator.num_pages
		categories = paginator.page(paginator.num_pages)

	return render(request, 'ledger/accounts/category/categories.html', locals())

def category(request, slug):
	category = get_object_or_404(Category, slug=slug)
	entries = category.entry_set.all().reverse()[:7]

	months = category.entry_set.dates('day', 'month')
	years = category.entry_set.dates('day', 'year')
	monthly = {}
	names = {month.strftime('%B %Y'):month.strftime('%Y-%m') for month in months}
	yearly = {}
	for entry in category.entry_set.all().order_by('day'):
		if not entry.account.name in monthly:
			monthly[entry.account.name] = {}
			for month in months:
				monthly[entry.account.name][month.strftime('%B %Y')] = 0

		if not entry.account.name in yearly:
			yearly[entry.account.name] = {}
			for year in years:
				yearly[entry.account.name][year.strftime('%Y')] = 0

		monthly[entry.account.name][entry.day.strftime('%B %Y')] = monthly[entry.account.name][entry.day.strftime('%B %Y')] + entry.amount
		yearly[entry.account.name][entry.day.strftime('%Y')] = yearly[entry.account.name][entry.day.strftime('%Y')] + entry.amount

	data_monthly = []
	for key, value in monthly.items():
		data = OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: names[t[0]]))
		data_monthly.append({'data':data, 'name':key})

	data_yearly = []
	for key, value in yearly.items():
		data = OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: t[0]))
		data_yearly.append({'data':data, 'name':key})

	return render(request, 'ledger/accounts/category/category.html', locals())

def entries(request, slug):
	category = get_object_or_404(Category, slug=slug)

	paginator = Paginator(category.entry_set.all().order_by('day'), 27)
	page = request.GET.get('page')
	try:
		entries = paginator.page(page)
		page = int(page)
	except PageNotAnInteger:
		page = paginator.num_pages
		entries = paginator.page(paginator.num_pages)
	except EmptyPage:
		page = paginator.num_pages
		entries = paginator.page(paginator.num_pages)

	try:
		last_prev = paginator.page(entries.previous_page_number()).object_list[24]
	except InvalidPage:
		last_prev = None

	try:
		first_next = paginator.page(entries.next_page_number()).object_list[0]
	except InvalidPage:
		first_next = None

	return render(request, 'ledger/accounts/category/entries.html', locals())