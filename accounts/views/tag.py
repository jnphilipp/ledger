from accounts.charts import tag_chart
from accounts.models import Tag, Unit
from collections import OrderedDict
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from json import dumps

def tags(request):
	tags = Tag.objects.all().extra(select={'lname':'lower(name)'}).order_by('lname')
	return render(request, 'ledger/accounts/tag/tags.html', locals())

def tag(request, slug):
	tag = get_object_or_404(Tag, slug=slug)
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in tag.entries.filter(account__unit=unit)), 2) for unit in set(tag.entries.values_list('account__unit', flat=True))}
	entries = tag.entries.all().order_by('day').reverse()[:5]
	monthly_data, yearly_data, library = tag_chart(tag)
	return render(request, 'ledger/accounts/tag/tag.html', locals())

def entries(request, slug):
	tag = get_object_or_404(Tag, slug=slug)
	totals = {Unit.objects.get(pk=unit):round(sum(entry.amount for entry in tag.entries.filter(account__unit=unit)), 2) for unit in set(tag.entries.values_list('account__unit', flat=True))}
	entries = tag.entries.all().order_by('day').reverse()
	return render(request, 'ledger/accounts/tag/entries.html', locals())