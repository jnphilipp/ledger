from accounts.models import Account, Category, Entry, Unit
from collections import defaultdict, OrderedDict

def account_chart(account, year=None, month=None, category=None):
	if year and month and category:
		series = defaultdict(int)
		for entry in account.entry_set.filter(day__year=year).filter(day__month=month).filter(category=category).order_by('day'):
			series[int(entry.day.strftime('%d'))] += entry.amount
		data = []
		if series:
			data.append({'data':OrderedDict(sorted(series.items(), key=lambda t: t[0])), 'name':category.name.lower()})

		library = {'plotOptions':{'column':{'stacking':'normal'}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'enabled':False}}

		return (data, library)
	elif year and month:
		categories = {}
		for category in Category.objects.filter(id__in=account.entry_set.filter(day__year=year).filter(day__month=month).values_list('category', flat=True)):
			categories[category] = 0
		for entry in account.entry_set.filter(day__year=year).filter(day__month=month).order_by('day'):
			categories[entry.category] += entry.amount
		data = []
		for key, value in categories.items():
			data.append({'data':{key.name.lower():value}, 'name':key.name.lower()})

		library = {'plotOptions':{'column':{'stacking':'normal'}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'valueDecimals':2, 'valueSuffix':account.unit.symbol}}

		return (data, library)
	elif year:
		months = account.entry_set.filter(day__year=year).dates('day', 'month')
		monthly = {}
		for category in Category.objects.filter(id__in=account.entry_set.filter(day__year=year).values_list('category', flat=True)):
			monthly[category] = {month.strftime('%B').lower():0 for month in months}
		names = OrderedDict(sorted({month.strftime('%B').lower():month.strftime('%m') for month in months}.items(), key=lambda t:t[1]))
		for entry in account.entry_set.filter(day__year=year).order_by('day'):
			monthly[entry.category][entry.day.strftime('%B').lower()] += entry.amount

		data = []
		for key, value in monthly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: names[t[0]])), 'name':key.name.lower()})

		library = {'plotOptions':{'column':{'stacking':'normal'}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':account.unit.symbol}}

		return (data, library)
	else:
		years = account.entry_set.dates('day', 'year')
		yearly = {}
		for category in Category.objects.filter(id__in=account.entry_set.values_list('category', flat=True)):
			yearly[category] = {year.strftime('%Y'):0 for year in years}
		for entry in account.entry_set.all().order_by('day'):
			yearly[entry.category][entry.day.strftime('%Y')] += entry.amount

		data = []
		for key, value in yearly.items():
			s = OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: t[0]))
			data.append({'data':s, 'name':key.name.lower()})

		library = {'plotOptions':{'column':{'stacking':'normal'}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':account.unit.symbol}}

		return (data, library)

def category_chart(category, ledger):
	units = Unit.objects.filter(id__in=set(category.entry_set.filter(account__ledger=ledger).values_list('account__unit', flat=True)))
	months = category.entry_set.filter(account__ledger=ledger).dates('day', 'month')
	years = category.entry_set.filter(account__ledger=ledger).dates('day', 'year')

	names = {month.strftime('%B %Y'):month.strftime('%Y-%m') for month in months}
	monthly = {account:{month.strftime('%B %Y'):0 for month in months} for account in Account.objects.filter(ledger=ledger).filter(id__in=category.entry_set.values_list('account', flat=True))}
	yearly = {account:{year.strftime('%Y'):0 for year in years} for account in Account.objects.filter(ledger=ledger).filter(id__in=category.entry_set.values_list('account', flat=True))}
	for entry in category.entry_set.filter(account__ledger=ledger).order_by('day'):
		monthly[entry.account][entry.day.strftime('%B %Y')] = monthly[entry.account][entry.day.strftime('%B %Y')] + entry.amount
		yearly[entry.account][entry.day.strftime('%Y')] = yearly[entry.account][entry.day.strftime('%Y')] + entry.amount

	monthly_data = []
	for key, value in monthly.items():
		monthly_data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: names[t[0]])), 'name':key.name})

	yearly_data = []
	for key, value in yearly.items():
		yearly_data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name})

	library = {'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'labels':{'rotation':-45}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % units[0].symbol if units.count() == 1 else ''}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % units[0].symbol if units.count() == 1 else ''}}, 'legend':{'enabled':False}, 'tooltip':{'shared':True, 'valueDecimals':2, 'valueSuffix':units[0].symbol if units.count() == 1 else ''}}

	return (monthly_data, yearly_data, library)

def tag_chart(tag, ledger):
	units = Unit.objects.filter(id__in=set(tag.entries.filter(account__ledger=ledger).values_list('account__unit', flat=True)))
	months = tag.entries.filter(account__ledger=ledger).dates('day', 'month')
	years = tag.entries.filter(account__ledger=ledger).dates('day', 'year')

	names = {month.strftime('%B %Y'):month.strftime('%Y-%m') for month in months}
	monthly = {account:{month.strftime('%B %Y'):0 for month in months} for account in Account.objects.filter(ledger=ledger).filter(id__in=tag.entries.values_list('account', flat=True))}
	yearly = {account:{year.strftime('%Y'):0 for year in years} for account in Account.objects.filter(ledger=ledger).filter(id__in=tag.entries.values_list('account', flat=True))}
	for entry in tag.entries.filter(account__ledger=ledger).order_by('day'):
		monthly[entry.account][entry.day.strftime('%B %Y')] = monthly[entry.account][entry.day.strftime('%B %Y')] + entry.amount
		yearly[entry.account][entry.day.strftime('%Y')] = yearly[entry.account][entry.day.strftime('%Y')] + entry.amount

	monthly_data = []
	for key, value in monthly.items():
		monthly_data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: names[t[0]])), 'name':key.name})

	yearly_data = []
	for key, value in yearly.items():
		yearly_data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name})

	library = {'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'labels':{'rotation':-45}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % units[0].symbol if units.count() == 1 else ''}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % units[0].symbol if units.count() == 1 else ''}}, 'legend':{'enabled':False}, 'tooltip':{'shared':True, 'valueDecimals':2, 'valueSuffix':units[0].symbol if units.count() == 1 else ''}}

	return (monthly_data, yearly_data, library)

def statistics_chart(unit, year=None, month=None):
	if month and year:
		days = Entry.objects.filter(account__in=Account.objects.filter(unit=unit)).filter(day__year=year).filter(day__month=month).dates('day', 'day')
		dayly = {}
		for category in Category.objects.filter(entry__account__unit=unit).filter(entry__day__year=year).filter(entry__day__month=month):
			dayly[category] = {int(day.strftime('%d')):0 for day in days}
		for entry in Entry.objects.filter(account__unit=unit).filter(day__year=year).filter(day__month=month):
			dayly[entry.category][int(entry.day.strftime('%d'))] += entry.amount

		data = []
		for key, value in dayly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name.lower()})

		library = {'plotOptions':{'column':{'stacking':'normal'}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)
	elif year:
		months = Entry.objects.filter(account__in=Account.objects.filter(unit=unit)).filter(day__year=year).dates('day', 'month')
		monthly = {}
		for category in Category.objects.filter(entry__account__unit=unit).filter(entry__day__year=year):
			monthly[category] = {month.strftime('%B').lower():0 for month in months}
		names = OrderedDict(sorted({month.strftime('%B').lower():month.strftime('%m') for month in months}.items(), key=lambda t:t[1]))
		for entry in Entry.objects.filter(account__unit=unit).filter(day__year=year):
			monthly[entry.category][entry.day.strftime('%B').lower()] += entry.amount

		data = []
		for key, value in monthly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: names[t[0]])), 'name':key.name.lower()})

		library = {'plotOptions':{'column':{'stacking':'normal'}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)
	else:
		years = Entry.objects.filter(account__in=Account.objects.filter(unit=unit)).dates('day', 'year')
		yearly = {}
		for category in Category.objects.filter(entry__account__unit=unit):
			yearly[category] = {year.strftime('%Y'):0 for year in years}
		for entry in Entry.objects.filter(account__unit=unit):
			yearly[entry.category][entry.day.strftime('%Y')] += entry.amount

		data = []
		for key, value in yearly.items():
			data.append({'data':OrderedDict(sorted({k: round(v, 2) for k, v in value.items()}.items(), key=lambda t: t[0])), 'name':key.name.lower()})

		library = {'plotOptions':{'column':{'stacking':'normal'}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':unit.symbol}}

		return (data, library)