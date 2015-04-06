from accounts.charts import tag_chart
from accounts.forms import TagForm
from accounts.models import Tag, Unit
from app.models import Ledger
from collections import OrderedDict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from json import dumps

@login_required(login_url='/login/')
def tags(request):
	ledger = get_object_or_404(Ledger, user=request.user)
	tags = Tag.objects.filter(entries__account__ledger=ledger).distinct().extra(select={'lname':'lower(accounts_tag.name)'}).order_by('lname')
	return render(request, 'ledger/accounts/tag/tags.html', locals())

@login_required(login_url='/login/')
def tag(request, slug):
	ledger = get_object_or_404(Ledger, user=request.user)
	tag = get_object_or_404(Tag, slug=slug)
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in tag.entries.filter(account__ledger=ledger).filter(account__unit=unit)), 2) for unit in set(tag.entries.filter(account__ledger=ledger).values_list('account__unit', flat=True))}
	entries = tag.entries.filter(account__ledger=ledger).order_by('day').reverse()[:5]
	monthly_data, yearly_data, library = tag_chart(tag, ledger)
	return render(request, 'ledger/accounts/tag/tag.html', locals())

@login_required(login_url='/login/')
def entries(request, slug):
	ledger = get_object_or_404(Ledger, user=request.user)
	tag = get_object_or_404(Tag, slug=slug)
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in tag.entries.filter(account__ledger=ledger).filter(account__unit=unit)), 2) for unit in set(tag.entries.filter(account__ledger=ledger).values_list('account__unit', flat=True))}
	entries = tag.entries.filter(account__ledger=ledger).order_by('day').reverse()
	return render(request, 'ledger/accounts/tag/entries.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def edit(request, slug):
	tag = get_object_or_404(Tag, slug=slug)
	if request.method == 'POST':
		form = TagForm(instance=tag, data=request.POST)
		if form.is_valid():
			tag = form.save()
			messages.add_message(request, messages.SUCCESS, 'the tag %s was successfully updated.' % tag.name.lower())
			return redirect('tag', slug=tag.slug)
		else:
			return render(request, 'ledger/accounts/tag/form.html', locals())
	else:
		form = TagForm(instance=tag)
		return render(request, 'ledger/accounts/tag/form.html', locals())

@login_required(login_url='/login/')
@csrf_protect
def delete(request, slug):
	tag = get_object_or_404(Tag, slug=slug)
	if request.method == 'POST':
		tag.delete()
		messages.add_message(request, messages.SUCCESS, 'the tag %s was successfully deleted.' % tag.name.lower())
		return redirect('tags')
	return render(request, 'ledger/accounts/tag/delete.html', locals())