from accounts.models import Tag
from collections import OrderedDict
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from json import dumps

def tags(request):
	paginator = Paginator(Tag.objects.all(), 28)
	page = request.GET.get('page')
	try:
		tags = paginator.page(page)
		page = int(page)
	except PageNotAnInteger:
		page = 1
		tags = paginator.page(1)
	except EmptyPage:
		page = paginator.num_pages
		tags = paginator.page(paginator.num_pages)

	return render(request, 'ledger/accounts/tag/tags.html', locals())

def tag(request, slug):
	tag = get_object_or_404(Tag, slug=slug)
	entries = tag.entries.all().reverse()[:5]

	months = tag.entries.dates('day', 'month')
	years = tag.entries.dates('day', 'year')
	monthly = {}
	names = {month.strftime('%B %Y'):month.strftime('%Y-%m') for month in months}
	yearly = {}
	for entry in tag.entries.all().order_by('day'):
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

	return render(request, 'ledger/accounts/tag/tag.html', locals())

def entries(request, slug):
	tag = get_object_or_404(Tag, slug=slug)

	paginator = Paginator(tag.entries.all().order_by('day'), 27)
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
		last_prev = paginator.page(entries.previous_page_number()).object_list[27]
	except InvalidPage:
		last_prev = None

	try:
		first_next = paginator.page(entries.next_page_number()).object_list[0]
	except InvalidPage:
		first_next = None

	return render(request, 'ledger/accounts/tag/entries.html', locals())