# -*- coding: utf-8 -*-

from accounts.forms import CategoryForm, CategoryFilterForm
from accounts.models import Category, Unit
from app.models import Ledger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

@login_required(login_url='/profile/signin/')
def categories(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    categories = Category.objects.filter(entries__account__ledger=ledger).distinct().extra(select={'lname':'lower(accounts_category.name)'}).order_by('lname')

    if request.method == 'POST':
        form = CategoryFilterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['accounts']:
                categories = categories.filter(entries__account__in=form.cleaned_data['accounts'])
            if form.cleaned_data['categories']:
                categories = categories.filter(id__in=form.cleaned_data['categories'])
            if form.cleaned_data['tags']:
                categories = categories.filter(entries__tags__in=form.cleaned_data['tags'])
    else:
        form = CategoryFilterForm()

    return render(request, 'ledger/accounts/category/categories.html', locals())

@login_required(login_url='/profile/signin/')
def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)
    year = request.GET.get('year')

    totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in category.entries.filter(account__ledger=ledger).filter(account__unit=unit)), 2) for unit in set(category.entries.filter(account__ledger=ledger).values_list('account__unit', flat=True))}
    entries = category.entries.filter(account__ledger=ledger).order_by('day').reverse()[:5]

    if not year:
        years = [y.strftime('%Y') for y in category.entries.filter(account__ledger=ledger).dates('day', 'year')]
    return render(request, 'ledger/accounts/category/category.html', locals())

@login_required(login_url='/profile/signin/')
def entries(request, slug):
    category = get_object_or_404(Category, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)
    totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in category.entries.filter(account__ledger=ledger).filter(account__unit=unit)), 2) for unit in set(category.entries.filter(account__ledger=ledger).values_list('account__unit', flat=True))}

    if request.method == 'POST':
        form = CategoryFilterForm(request.POST)
        entry_list = category.entries.all().reverse()
        if form.is_valid():
            if form.cleaned_data['accounts']:
                entry_list = entry_list.filter(account__in=form.cleaned_data['accounts'])
            if form.cleaned_data['tags']:
                entry_list = entry_list.filter(tags__in=form.cleaned_data['tags'])
    else:
        form = CategoryFilterForm()
        entry_list = category.entries.filter(account__ledger=ledger).order_by('day').reverse()

    paginator = Paginator(entry_list, 200)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    return render(request, 'ledger/accounts/category/entries.html', locals())

@login_required(login_url='/profile/signin/')
def statistics(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    category = get_object_or_404(Category, slug=slug)
    year = request.GET.get('year')

    if not year:
        years = [y.strftime('%Y') for y in category.entries.filter(account__ledger=ledger).dates('day', 'year')]
    return render(request, 'ledger/accounts/category/statistics.html', locals())

@login_required(login_url='/profile/signin/')
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

@login_required(login_url='/profile/signin/')
@csrf_protect
def delete(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.add_message(request, messages.SUCCESS, 'the category %s was successfully deleted.' % category.name.lower())
        return redirect('categories')
    return render(request, 'ledger/accounts/category/delete.html', locals())
