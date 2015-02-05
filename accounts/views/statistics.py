from accounts.charts import statistics_chart
from accounts.models import Category, Entry, Account, Unit
from collections import OrderedDict
from datetime import date
from django.db.models import Count, Q
from django.shortcuts import render

def statistics(request):
	unit_slug = request.GET.get('unit')
	year = request.GET.get('year')
	month = request.GET.get('month')
	if year and month:
		month_name = date(year=int(year), month=int(month), day=1).strftime('%B').lower()

	units = Unit.objects.filter(slug=unit_slug) if unit_slug else Unit.objects.all()
	datas = {}
	libraries = {}
	for unit in units:
		data, library = statistics_chart(unit, year=year, month=month)
		datas[unit] = data
		libraries[unit] = library

	if unit_slug:
		years = Entry.objects.filter(account__in=Account.objects.filter(unit=units.first())).dates('day', 'year')
		if year:
			months = Entry.objects.filter(account__in=Account.objects.filter(unit=units.first())).filter(day__year=year).dates('day', 'month')

	return render(request, 'ledger/accounts/statistics/statistics.html', locals())