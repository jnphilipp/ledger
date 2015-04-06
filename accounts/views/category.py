from accounts.charts import category_chart
from accounts.forms import CategoryForm
from accounts.models import Category, Unit
from app.models import Ledger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

@login_required(login_url='/login/')
def categories(request):
	ledger = get_object_or_404(Ledger, user=request.user)
	categories = Category.objects.filter(entry__account__ledger=ledger).distinct().extra(select={'lname':'lower(accounts_category.name)'}).order_by('lname')
	return render(request, 'ledger/accounts/category/categories.html', locals())

@login_required(login_url='/login/')
def category(request, slug):
	category = get_object_or_404(Category, slug=slug)
	ledger = get_object_or_404(Ledger, user=request.user)
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in category.entry_set.filter(account__ledger=ledger).filter(account__unit=unit)), 2) for unit in set(category.entry_set.filter(account__ledger=ledger).values_list('account__unit', flat=True))}
	entries = category.entry_set.filter(account__ledger=ledger).order_by('day').reverse()[:5]
	monthly_data, yearly_data, library = category_chart(category, ledger)
	return render(request, 'ledger/accounts/category/category.html', locals())

@login_required(login_url='/login/')
def entries(request, slug):
	category = get_object_or_404(Category, slug=slug)
	ledger = get_object_or_404(Ledger, user=request.user)
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in category.entry_set.filter(account__ledger=ledger).filter(account__unit=unit)), 2) for unit in set(category.entry_set.filter(account__ledger=ledger).values_list('account__unit', flat=True))}

	entries = category.entry_set.filter(account__ledger=ledger).order_by('day').reverse()

	return render(request, 'ledger/accounts/category/entries.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def edit(request, slug):
	category = get_object_or_404(Category, slug=slug)
	if request.method == 'POST':
		form = CategoryForm(instance=category, data=request.POST)
		if form.is_valid():
			category = form.save()
			messages.add_message(request, messages.SUCCESS, 'the category %s was successfully updated.' % category.name.lower())
			return redirect('category', slug=category.slug)
		else:
			return render(request, 'ledger/accounts/category/form.html', locals())
	else:
		form = CategoryForm(instance=category)
		return render(request, 'ledger/accounts/category/form.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def delete(request, slug):
	category = get_object_or_404(Category, slug=slug)
	if request.method == 'POST':
		category.delete()
		messages.add_message(request, messages.SUCCESS, 'the category %s was successfully deleted.' % category.name.lower())
		return redirect('categories')
	return render(request, 'ledger/accounts/category/delete.html', locals())