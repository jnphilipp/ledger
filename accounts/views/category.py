from accounts.charts import category_chart
from accounts.models import Category, Unit
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

def categories(request):
	paginator = Paginator(Category.objects.all().extra(select={'lname':'LOWER(name)'}).order_by('lname'), 28)
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
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in category.entry_set.filter(account__unit=unit)), 2) for unit in set(category.entry_set.values_list('account__unit', flat=True))}
	entries = category.entry_set.all().order_by('day').reverse()[:5]
	monthly_data, yearly_data, library = category_chart(category)
	return render(request, 'ledger/accounts/category/category.html', locals())

def entries(request, slug):
	category = get_object_or_404(Category, slug=slug)
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in category.entry_set.filter(account__unit=unit)), 2) for unit in set(category.entry_set.values_list('account__unit', flat=True))}

	paginator = Paginator(category.entry_set.all().order_by('day'), 25)
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