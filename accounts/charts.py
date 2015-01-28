from accounts.models import Unit
from collections import OrderedDict

def category_chart(category):
	units = Unit.objects.filter(id__in=set(category.entry_set.values_list('account__unit', flat=True)))
	months = category.entry_set.dates('day', 'month')
	years = category.entry_set.dates('day', 'year')

	names = {month.strftime('%B %Y'):month.strftime('%Y-%m') for month in months}
	monthly = {}
	yearly = {}
	for entry in category.entry_set.all().order_by('day'):
		if not entry.account in monthly:
			monthly[entry.account] = {}
			for month in months:
				monthly[entry.account][month.strftime('%B %Y')] = 0

		if not entry.account in yearly:
			yearly[entry.account] = {}
			for year in years:
				yearly[entry.account][year.strftime('%Y')] = 0

		monthly[entry.account][entry.day.strftime('%B %Y')] = monthly[entry.account][entry.day.strftime('%B %Y')] + entry.amount
		yearly[entry.account][entry.day.strftime('%Y')] = yearly[entry.account][entry.day.strftime('%Y')] + entry.amount

	monthly_data = []
	for key, value in monthly.items():
		data = OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: names[t[0]]))
		monthly_data.append({'data':data, 'name':key.name})

	yearly_data = []
	for key, value in yearly.items():
		data = OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: t[0]))
		yearly_data.append({'data':data, 'name':key.name})


	library = {'plotOptions':{'column':{'stacking':'normal', 'dataLabels':{'enabled':True, 'color':'white', 'style':{'textShadow':'0 0 3px black'}, 'format':'{point.y:.2f} %s' % units[0].symbol if units.count() == 1 else ''}}}, 'xAxis':{'labels':{'rotation':-45}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % units[0].symbol if units.count() == 1 else ''}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % units[0].symbol if units.count() == 1 else ''}}, 'legend':{'enabled':False}, 'tooltip':{'shared':True, 'valueDecimals':2, 'valueSuffix':units[0].symbol if units.count() == 1 else ''}}

	return (monthly_data, yearly_data, library)

def tag_chart(tag):
	units = Unit.objects.filter(id__in=set(tag.entries.values_list('account__unit', flat=True)))
	months = tag.entries.dates('day', 'month')
	years = tag.entries.dates('day', 'year')

	names = {month.strftime('%B %Y'):month.strftime('%Y-%m') for month in months}
	monthly = {}
	yearly = {}
	for entry in tag.entries.all().order_by('day'):
		if not entry.account in monthly:
			monthly[entry.account] = {}
			for month in months:
				monthly[entry.account][month.strftime('%B %Y')] = 0

		if not entry.account in yearly:
			yearly[entry.account] = {}
			for year in years:
				yearly[entry.account][year.strftime('%Y')] = 0

		monthly[entry.account][entry.day.strftime('%B %Y')] = monthly[entry.account][entry.day.strftime('%B %Y')] + entry.amount
		yearly[entry.account][entry.day.strftime('%Y')] = yearly[entry.account][entry.day.strftime('%Y')] + entry.amount

	monthly_data = []
	for key, value in monthly.items():
		data = OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: names[t[0]]))
		monthly_data.append({'data':data, 'name':key.name})

	yearly_data = []
	for key, value in yearly.items():
		data = OrderedDict(sorted({k: round(v, 2) if v != 0 else None for k, v in value.items()}.items(), key=lambda t: t[0]))
		yearly_data.append({'data':data, 'name':key.name})

	library = {'plotOptions':{'column':{'stacking':'normal', 'dataLabels':{'enabled':True, 'color':'white', 'style':{'textShadow':'0 0 3px black'}, 'format':'{point.y:.2f} %s' % units[0].symbol if units.count() == 1 else ''}}}, 'xAxis':{'labels':{'rotation':-45}}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % units[0].symbol if units.count() == 1 else ''}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % units[0].symbol if units.count() == 1 else ''}}, 'legend':{'enabled':False}, 'tooltip':{'shared':True, 'valueDecimals':2, 'valueSuffix':units[0].symbol if units.count() == 1 else ''}}

	return (monthly_data, yearly_data, library)