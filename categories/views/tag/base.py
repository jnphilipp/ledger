# -*- coding: utf-8 -*-

from accounts.models import Entry
from categories.forms import TagForm, FilterForm
from categories.models import Tag
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from users.models import Ledger


@login_required
def list(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    tags = Tag.objects.filter(
        entries__account__ledger=ledger).distinct().extra(select={
            'lname': 'lower(categories_tag.name)'}).order_by('lname')

    if request.method == 'POST':
        form = FilterForm(request.POST)
        del form.fields['start_date']
        del form.fields['end_date']
        if form.is_valid():
            if form.cleaned_data['accounts']:
                tags = tags.filter(
                    entries__account__in=form.cleaned_data['accounts'])
            if form.cleaned_data['categories']:
                tags = tags.filter(
                    entries__category__in=form.cleaned_data['categories'])
            if form.cleaned_data['tags']:
                tags = tags.filter(id__in=form.cleaned_data['tags'])
            if form.cleaned_data['units']:
                tags = tags.filter(
                    entries__account__unit__in=form.cleaned_data['units'])
    else:
        form = FilterForm()
        del form.fields['start_date']
        del form.fields['end_date']
    return render(request, 'categories/tag/list.html', locals())


@login_required
def detail(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    tag = get_object_or_404(Tag, slug=slug)
    year = request.GET.get('year')

    entry_list = tag.entries.filter(account__ledger=ledger)
    entries = entry_list.order_by('day').reverse()[:5]

    if not year:
        years = tag.entries.filter(account__ledger=ledger).dates('day', 'year')
        years = [y.strftime('%Y') for y in years]
    return render(request, 'categories/tag/detail.html', locals())


@login_required
def entries(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    tag = get_object_or_404(Tag, slug=slug)
    entry_list = tag.entries.filter(account__ledger=ledger).order_by('-day')

    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['start_date']:
                entry_list = entry_list.filter(
                    day__gte=form.cleaned_data['start_date'])
            if form.cleaned_data['end_date']:
                entry_list = entry_list.filter(
                    day__lte=form.cleaned_data['end_date'])
            if form.cleaned_data['accounts']:
                entry_list = entry_list.filter(
                    account__in=form.cleaned_data['accounts'])
            if form.cleaned_data['categories']:
                entry_list = entry_list.filter(
                    category__in=form.cleaned_data['categories'])
            if form.cleaned_data['tags']:
                entry_list = entry_list.filter(
                    tags__in=form.cleaned_data['tags'])
            if form.cleaned_data['units']:
                entry_list = entry_list.filter(
                    account__unit__in=form.cleaned_data['units'])
    else:
        form = FilterForm()

    paginator = Paginator(entry_list, 200)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    content_type = ContentType.objects.get_for_model(Entry)
    return render(request, 'categories/tag/entries.html', locals())


@login_required
def statistics(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    tag = get_object_or_404(Tag, slug=slug)
    chart = request.GET.get('chart')
    year = request.GET.get('year')

    if chart == 'accounts':
        chart_name = _('Accounts')
    elif chart == 'categories':
        chart_name = _('Categories')

    if chart and not year:
        years = tag.entries.filter(account__ledger=ledger).dates('day', 'year')
        years = [y.strftime('%Y') for y in years]
    return render(request, 'categories/tag/statistics.html', locals())


@login_required
@csrf_protect
def add(request):
    return _add(request, 'categories/tag/form.html')


@login_required
@csrf_protect
def add_another(request):
    return _add(request, 'categories/tag/add_another.html', False,
                request.GET.get('target_id'))


def _add(request, template, do_redirect=True, target_id=None):
    if request.method == 'POST':
        form = TagForm(data=request.POST)
        if form.is_valid():
            tag = form.save()
            msg = _('The tag "%(name)s" was successfully created.')
            messages.add_message(request, messages.SUCCESS,
                                 msg % {'name': tag.name})
            if do_redirect:
                return redirect('categories:tag', slug=tag.slug)
    else:
        form = TagForm()
    return render(request, template, locals())


@login_required
@csrf_protect
def edit(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    if request.method == 'POST':
        form = TagForm(instance=tag, data=request.POST)
        if form.is_valid():
            tag = form.save()
            msg = _('The tag "%(name)s" was successfully updated.')
            messages.add_message(request, messages.SUCCESS,
                                 msg % {'name': tag.name})
            return redirect('categories:tag', slug=tag.slug)
    else:
        form = TagForm(instance=tag)
    return render(request, 'categories/tag/form.html', locals())


@login_required
@csrf_protect
def delete(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    if request.method == 'POST':
        tag.delete()
        msg = _('The tag "%(name)s" was successfully deleted.')
        messages.add_message(request, messages.SUCCESS,
                             msg % {'name': tag.name})
        return redirect('categories:tags')
    return render(request, 'categories/tag/delete.html', locals())
