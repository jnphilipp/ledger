from accounts.models import Category
from collections import defaultdict, OrderedDict
from django.db.models import Q

def account_chart(account, year=None, month=None, category=None):
	if year and month and category:
		series = defaultdict(int)
		for entry in account.entry_set.filter(day__year=year).filter(day__month=month).filter(category=category).order_by('day'):
			series[int(entry.day.strftime('%d'))] += entry.amount
		data = []
		if series:
			data.append({'data':OrderedDict(sorted(series.items(), key=lambda t: t[0])), 'name':category.name.lower()})

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'enabled':False}}

		return (data, library)
	elif year and month:
		categories = {}
		for category in Category.objects.filter(id__in=account.entry_set.filter(Q(day__year=year) & Q(day__month=month)).values_list('category', flat=True)):
			categories[category] = 0
		for entry in account.entry_set.filter(day__year=year).filter(day__month=month).order_by('day'):
			categories[entry.category] += entry.amount
		data = []
		for key, value in categories.items():
			data.append({'data':{key.name.lower():value}, 'name':key.name.lower()})

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'valueDecimals':2, 'valueSuffix':account.unit.symbol}}

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

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':account.unit.symbol}}

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

		library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % account.unit.symbol}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % account.unit.symbol}}, 'legend':{'enabled':False}, 'tooltip':{'shared':False, 'valueDecimals':2, 'valueSuffix':account.unit.symbol}}

		return (data, library)