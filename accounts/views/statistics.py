from accounts.charts import statistics_chart
from accounts.models import Category, Entry, Account, Unit
from app.models import Ledger
from collections import OrderedDict
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

@login_required(login_url='/login/')
def statistics(request):
	chart_type = request.GET.get('type')
	unit_slug = request.GET.get('unit')
	year = request.GET.get('year')
	month = request.GET.get('month')
	if year and month:
		month_name = date(year=int(year), month=int(month), day=1).strftime('%B').lower()

	ledger = get_object_or_404(Ledger, user=request.user)
	if not chart_type:
		option_name = 'type'
		options = [{'id':'categories', 'key':'type', 'value':'categories'}, {'id':'tags', 'key':'type', 'value':'tags'}]
	elif chart_type and not unit_slug:
		option_name = 'unit'
		options = [{'id':unit.slug, 'key':'unit', 'value':unit.name.lower()} for unit in Unit.objects.filter(account__ledger=ledger).distinct()]
	elif chart_type and unit_slug and not year:
		unit = get_object_or_404(Unit, slug=unit_slug)

		years = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).dates('day', 'year')
		if chart_type == 'tags':
			years = years.filter(tags__isnull=False)

		option_name = 'year'
		options = [{'id':year.strftime('%Y'), 'key':'year', 'value':year.strftime('%Y')} for year in years]
		data, library = statistics_chart(chart_type, unit, ledger)
	elif chart_type and unit_slug and year and not month:
		unit = get_object_or_404(Unit, slug=unit_slug)

		months = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).filter(day__year=year).dates('day', 'month')
		if chart_type == 'tags':
			months = months.filter(tags__isnull=False)

		option_name = 'month'
		options = [{'id':month.strftime('%m'), 'key':'month', 'value':month.strftime('%B').lower()} for month in months]
		data, library = statistics_chart(chart_type, unit, ledger, year=year)
	elif chart_type and unit_slug and year and month:
		unit = get_object_or_404(Unit, slug=unit_slug)
		option_name = None
		options = []
		data, library = statistics_chart(chart_type, unit, ledger, year=year, month=month)
	else:
		options = []

	return render(request, 'ledger/accounts/statistics/statistics.html', locals())