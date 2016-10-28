# -*- coding: utf-8 -*-

from categories.forms import CategoryForm, FilterForm
from categories.models import Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from units.models import Unit
from users.models import Ledger


@login_required
def categories(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    categories = Category.objects.filter(Q(entries__account__ledger=ledger) | Q(accounts__ledger=ledger)).distinct().extra(select={'lname':'lower(categories_category.name)'}).order_by('lname')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        del form.fields['start_date']
        del form.fields['end_date']
        if form.is_valid():
            if form.cleaned_data['accounts']:
                categories = categories.filter(entries__account__in=form.cleaned_data['accounts'])
            if form.cleaned_data['categories']:
                categories = categories.filter(id__in=form.cleaned_data['categories'])
            if form.cleaned_data['tags']:
                categories = categories.filter(entries__tags__in=form.cleaned_data['tags'])
            if form.cleaned_data['units']:
                categories = categories.filter(entries__account__unit__in=form.cleaned_data['units'])
    else:
        form = FilterForm()
        del form.fields['start_date']
        del form.fields['end_date']
    return render(request, 'categories/category/categories.html', locals())


@login_required
def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)
    year = request.GET.get('year')

    entry_list = category.entries.filter(account__ledger=ledger)
    entries = entry_list.order_by('day').reverse()[:5]

    if not year:
        years = [y.strftime('%Y') for y in category.entries.filter(account__ledger=ledger).dates('day', 'year')]
    return render(request, 'categories/category/category.html', locals())


@login_required
def entries(request, slug):
    category = get_object_or_404(Category, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)

    if request.method == 'POST':
        form = FilterForm(request.POST)
        del form.fields['categories']
        entry_list = category.entries.filter(account__ledger=ledger).order_by('day').reverse()
        if form.is_valid():
            if form.cleaned_data['start_date']:
                entry_list = entry_list.filter(day__gte=form.cleaned_data['start_date'])
            if form.cleaned_data['end_date']:
                entry_list = entry_list.filter(day__lte=form.cleaned_data['end_date'])
            if form.cleaned_data['accounts']:
                entry_list = entry_list.filter(account__in=form.cleaned_data['accounts'])
            if form.cleaned_data['tags']:
                entry_list = entry_list.filter(tags__in=form.cleaned_data['tags'])
            if form.cleaned_data['tags']:
                entry_list = entry_list.filter(account__unit__in=form.cleaned_data['units'])
    else:
        form = FilterForm()
        del form.fields['categories']
        entry_list = category.entries.filter(account__ledger=ledger).order_by('day').reverse()


    paginator = Paginator(entry_list, 200)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    return render(request, 'categories/category/entries.html', locals())


@login_required
def statistics(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    category = get_object_or_404(Category, slug=slug)
    year = request.GET.get('year')
    if not year:
        years = [y.strftime('%Y') for y in category.entries.filter(account__ledger=ledger).dates('day', 'year')]
    return render(request, 'categories/category/statistics.html', locals())


@login_required
@csrf_protect
def add(request):
    return _add(request, 'categories/category/form.html')


@login_required
@csrf_protect
def add_another(request):
    return _add(request, 'categories/category/add_another.html', False, request.GET.get('target_id'))


def _add(request, template, do_redirect=True, target_id=None):
    if request.method == 'POST':
        form = CategoryForm(data=request.POST)
        if form.is_valid():
            category = form.save()
            messages.add_message(request, messages.SUCCESS, _('the category "%(name)s" was successfully created.') % {'name': category.name.lower()})
            if do_redirect:
                return redirect('category', slug=category.slug)
        return render(request, template, locals())
    else:
        form = CategoryForm()
    return render(request, template, locals())


@login_required
@csrf_protect
def edit(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = CategoryForm(instance=category, data=request.POST)
        if form.is_valid():
            category = form.save()
            messages.add_message(request, messages.SUCCESS, _('the category "%(name)s" was successfully updated.') % {'name': category.name.lower()})
            return redirect('category', slug=category.slug)
        return render(request, 'categories/category/form.html', locals())
    else:
        form = CategoryForm(instance=category)
    return render(request, 'categories/category/form.html', locals())


@login_required
@csrf_protect
def delete(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.add_message(request, messages.SUCCESS, _('the category "%(name)s" was successfully deleted.') % {'name': category.name.lower()})
        return redirect('categories')
    return render(request, 'categories/category/delete.html', locals())
