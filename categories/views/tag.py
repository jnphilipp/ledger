# -*- coding: utf-8 -*-

from categories.forms import TagForm#, TagFilterForm
# from accounts.models import Tag, Unit
# from app.models import Ledger
# from collections import OrderedDict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
# from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
# from json import dumps

@login_required(login_url='/profile/signin/')
def tags(request):
    pass
    # ledger = get_object_or_404(Ledger, user=request.user)
    # tags = Tag.objects.filter(entries__account__ledger=ledger).distinct().extra(select={'lname':'lower(accounts_tag.name)'}).order_by('lname')

    # if request.method == 'POST':
    #     form = TagFilterForm(request.POST)
    #     if form.is_valid():
    #         if form.cleaned_data['accounts']:
    #             tags = tags.filter(entries__account__in=form.cleaned_data['accounts'])
    #         if form.cleaned_data['categories']:
    #             tags = tags.filter(entries__category__in=form.cleaned_data['categories'])
    #         if form.cleaned_data['tags']:
    #             tags = tags.filter(id__in=form.cleaned_data['tags'])
    # else:
    #     form = TagFilterForm()

    # return render(request, 'ledger/accounts/tag/tags.html', locals())

@login_required(login_url='/profile/signin/')
def tag(request, slug):
    pass
    # ledger = get_object_or_404(Ledger, user=request.user)
    # tag = get_object_or_404(Tag, slug=slug)
    # year = request.GET.get('year')

    # totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in tag.entries.filter(account__ledger=ledger).filter(account__unit=unit)), 2) for unit in set(tag.entries.filter(account__ledger=ledger).values_list('account__unit', flat=True))}
    # entries = tag.entries.filter(account__ledger=ledger).order_by('day').reverse()[:5]

    # if not year:
    #     years = [y.strftime('%Y') for y in tag.entries.filter(account__ledger=ledger).dates('day', 'year')]
    # return render(request, 'ledger/accounts/tag/tag.html', locals())

# @login_required(login_url='/profile/signin/')
# def entries(request, slug):
#     ledger = get_object_or_404(Ledger, user=request.user)
#     tag = get_object_or_404(Tag, slug=slug)

#     if request.method == 'POST':
#         form = TagFilterForm(request.POST)
#         entry_list = tag.entries.all().reverse()
#         if form.is_valid():
#             if form.cleaned_data['start_date']:
#                 entry_list = entry_list.filter(day__gte=form.cleaned_data['start_date'])
#             if form.cleaned_data['end_date']:
#                 entry_list = entry_list.filter(day__lte=form.cleaned_data['end_date'])
#             if form.cleaned_data['accounts']:
#                 entry_list = entry_list.filter(account__in=form.cleaned_data['accounts'])
#             if form.cleaned_data['categories']:
#                 entry_list = entry_list.filter(category__in=form.cleaned_data['categories'])
#             if form.cleaned_data['tags']:
#                 entry_list = entry_list.filter(tags__in=form.cleaned_data['tags'])
#     else:
#         form = TagFilterForm()
#         entry_list = tag.entries.filter(account__ledger=ledger).order_by('day').reverse()

#     totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in entry_list.filter(account__unit=unit)), 2) for unit in set(entry_list.values_list('account__unit', flat=True))}

#     paginator = Paginator(entry_list, 200)
#     page = request.GET.get('page')
#     try:
#         entries = paginator.page(page)
#     except PageNotAnInteger:
#         entries = paginator.page(1)
#     except EmptyPage:
#         entries = paginator.page(paginator.num_pages)

#     return render(request, 'ledger/accounts/tag/entries.html', locals())

# @login_required(login_url='/profile/signin/')
# def statistics(request, slug):
#     ledger = get_object_or_404(Ledger, user=request.user)
#     tag = get_object_or_404(Tag, slug=slug)
#     chart = request.GET.get('chart')
#     year = request.GET.get('year')

#     if chart and not year:
#         years = [y.strftime('%Y') for y in tag.entries.filter(account__ledger=ledger).dates('day', 'year')]
#     return render(request, 'ledger/accounts/tag/statistics.html', locals())


@login_required(login_url='/users/signin/')
@csrf_protect
def add(request):
    return _add(request, 'categories/tag/add.html')


@login_required(login_url='/users/signin/')
@csrf_protect
def add_another(request):
    return _add(request, 'categories/tag/add_another.html', False)


def _add(request, template, do_redirect=True):
    if request.method == 'POST':
        form = TagForm(data=request.POST)
        if form.is_valid():
            tag = form.save()
            messages.add_message(request, messages.SUCCESS, _('the tag %(name)s was successfully created.') % {'name': tag.name.lower()})
            if do_redirect:
                return redirect('tag', slug=tag.slug)
        return render(request, template, locals())
    else:
        form = TagForm()
        return render(request, template, locals())


@login_required(login_url='/profile/signin/')
@csrf_protect
def edit(request, slug):
    pass
    # tag = get_object_or_404(Tag, slug=slug)
    # if request.method == 'POST':
    #     form = TagForm(instance=tag, data=request.POST)
    #     if form.is_valid():
    #         tag = form.save()
    #         messages.add_message(request, messages.SUCCESS, 'the tag %s was successfully updated.' % tag.name.lower())
    #         return redirect('tag', slug=tag.slug)
    #     else:
    #         return render(request, 'ledger/accounts/tag/form.html', locals())
    # else:
    #     form = TagForm(instance=tag)
    #     return render(request, 'ledger/accounts/tag/form.html', locals())


@login_required(login_url='/profile/signin/')
@csrf_protect
def delete(request, slug):
    pass
    # tag = get_object_or_404(Tag, slug=slug)
    # if request.method == 'POST':
    #     tag.delete()
    #     messages.add_message(request, messages.SUCCESS, 'the tag %s was successfully deleted.' % tag.name.lower())
    #     return redirect('tags')
    # return render(request, 'ledger/accounts/tag/delete.html', locals())
