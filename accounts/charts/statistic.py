from accounts.models import Category, Entry, Tag
from collections import OrderedDict
from django.db.models import Q

def statistics_chart(chart_type, unit, ledger, year=None, month=None):
	if chart_type == 'categories':
		return categories_statistics_chart(unit, ledger, year, month)
	elif chart_type == 'tags':
		return tags_statistics_chart(unit, ledger, year, month)
	else:
		return None

def categories_statistics_chart(unit, ledger, year=None, month=None):
	if month and year:
		days = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year) & Q(day__month=month)).dates('day', 'day')
		dayly = {}
		for category in Category.objects.exclude(account__in=ledger.accounts.all()).filter(Q(entry__account__in=ledger.accounts.all()) & Q(entry__account__unit=unit) & Q(entry__day__year=year) & Q(entry__day__month=month)).distinct():
			dayly[category] = {int(day.strftime('%d')):0 for day in days}
		for entry in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=month)):
			if entry.category in dayly.keys():
				dayly[entry.category][int(entry.day.strftime('%d'))] += entry.amount

		data = []
		for key, value in dayly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name.lower()})

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)
	elif year:
		months = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year)).dates('day', 'month')
		monthly = {}
		for category in Category.objects.exclude(account__in=ledger.accounts.all()).filter(Q(entry__account__in=ledger.accounts.all()) & Q(entry__account__unit=unit) & Q(entry__day__year=year)).distinct():
			monthly[category] = {month.strftime('%B').lower():0 for month in months}
		names = OrderedDict(sorted({month.strftime('%B').lower():month.strftime('%m') for month in months}.items(), key=lambda t:t[1]))
		for entry in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year)):
			if entry.category in monthly.keys():
				monthly[entry.category][entry.day.strftime('%B').lower()] += entry.amount

		data = []
		for key, value in monthly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: names[t[0]])), 'name':key.name.lower()})

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)
	else:
		years = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).dates('day', 'year')
		yearly = {}
		for category in Category.objects.exclude(account__in=ledger.accounts.all()).filter(Q(entry__account__in=ledger.accounts.all()) & Q(entry__account__unit=unit)).distinct():
			yearly[category] = {year.strftime('%Y'):0 for year in years}
		for entry in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit)):
			if entry.category in yearly.keys():
				yearly[entry.category][entry.day.strftime('%Y')] += entry.amount

		data = []
		for key, value in yearly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name.lower()})

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)

def tags_statistics_chart(unit, ledger, year=None, month=None):
	if month and year:
		days = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year) & Q(day__month=month) & Q(tags__isnull=False)).dates('day', 'day')
		dayly = {}
		for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct():
			dayly[tag] = {int(day.strftime('%d')):0 for day in days}
		for entry in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=month)):
			for tag in entry.tags.all():
				if tag in dayly.keys():
					dayly[tag][int(entry.day.strftime('%d'))] += entry.amount

		data = []
		for key, value in dayly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name.lower()})

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)
	elif year:
		months = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year) & Q(tags__isnull=False)).dates('day', 'month')
		monthly = {}
		for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year)).distinct():
			monthly[tag] = {month.strftime('%B').lower():0 for month in months}
		names = OrderedDict(sorted({month.strftime('%B').lower():month.strftime('%m') for month in months}.items(), key=lambda t:t[1]))
		for entry in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year)):
			for tag in entry.tags.all():
				if tag in monthly.keys():
					monthly[tag][entry.day.strftime('%B').lower()] += entry.amount

		data = []
		for key, value in monthly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: names[t[0]])), 'name':key.name.lower()})

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)
	else:
		years = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).filter(tags__isnull=False).dates('day', 'year')
		yearly = {}
		for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit)).distinct():
			yearly[tag] = {year.strftime('%Y'):0 for year in years}
		for entry in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit)):
			for tag in entry.tags.all():
				if tag in yearly.keys():
					yearly[tag][entry.day.strftime('%Y')] += entry.amount

		data = []
		for key, value in yearly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name.lower()})
		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)