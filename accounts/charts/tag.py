from accounts.models import Account, Unit
from collections import OrderedDict
from copy import deepcopy
from django.db.models import Sum

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

	library = {'chart':{'zoomType':'x'}, 'plotOptions':{'column':{'stacking':'normal'}}, 'xAxis':{'labels':{'rotation':-45}, 'crosshair':True}, 'yAxis':{'stackLabels':{'enabled':True, 'style':{'fontWeight':'bold', 'color':"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"}, 'format':'{total:.2f} %s' % units[0].symbol if units.count() == 1 else ''}, 'plotLines':[{'value':0, 'color':'#ff0000', 'width':1, 'zIndex':1}], 'labels':{'format':'{value:.2f} %s' % units[0].symbol if units.count() == 1 else ''}}, 'legend':{'enabled':False}, 'tooltip':{'shared':True, 'valueDecimals':2, 'valueSuffix':units[0].symbol if units.count() == 1 else ''}}

	ml = deepcopy(library)
	avg_month = tag.entries.filter(account__ledger=ledger).aggregate(Sum('amount'))['amount__sum'] / len(monthly_data[0]['data']) if monthly_data else 0
	ml['yAxis']['plotLines'].append({'value':avg_month, 'color':'#00ff00', 'width':3, 'zIndex':4, 'label':{'text':'average: %s%s' % (round(avg_month, 2), units[0].symbol if units.count() == 1 else ''), 'y':13}})

	yl = deepcopy(library)
	avg_year = tag.entries.filter(account__ledger=ledger).aggregate(Sum('amount'))['amount__sum'] / len(yearly_data[0]['data']) if yearly_data else 0
	yl['yAxis']['plotLines'].append({'value':avg_year, 'color':'#00ff00', 'width':3, 'zIndex':4, 'label':{'text':'average: %s%s' % (round(avg_year, 2), units[0].symbol if units.count() == 1 else ''), 'y':13}})

	return (monthly_data, yearly_data, ml, yl)