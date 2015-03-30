from accounts.charts import category_chart
from accounts.models import Category, Unit
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

def categories(request):
	categories = Category.objects.all().extra(select={'lname':'LOWER(name)'}).order_by('lname')
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

	entries = category.entry_set.all().order_by('day').reverse()

	return render(request, 'ledger/accounts/category/entries.html', locals())