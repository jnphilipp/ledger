from accounts.charts import statistics_chart
from accounts.models import Category, Entry, Account, Unit
from app.models import Ledger
from collections import OrderedDict
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

@login_required(login_url='/login/')
def statistics(request):
	unit_slug = request.GET.get('unit')
	year = request.GET.get('year')
	month = request.GET.get('month')
	if year and month:
		month_name = date(year=int(year), month=int(month), day=1).strftime('%B').lower()

	ledger = get_object_or_404(Ledger, user=request.user)
	units = Unit.objects.filter(account__ledger=ledger).distinct().filter(slug=unit_slug) if unit_slug else Unit.objects.filter(account__ledger=ledger).distinct()
	datas = {}
	libraries = {}
	for unit in units:
		data, library = statistics_chart(unit, ledger, year=year, month=month)
		if data:
			datas[unit] = data
			libraries[unit] = library

	if unit_slug:
		years = Entry.objects.filter(account__in=ledger.accounts.filter(unit=units.first())).dates('day', 'year')
		if year:
			months = Entry.objects.filter(account__in=ledger.accounts.filter(unit=units.first())).filter(day__year=year).dates('day', 'month')

	return render(request, 'ledger/accounts/statistics/statistics.html', locals())