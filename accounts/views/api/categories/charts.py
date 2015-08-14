from accounts.models import Account, Category, Unit
from app.models import Ledger
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from json import dumps

@login_required(login_url='/profile/signin/')
def statistics(request, slug):
    year = request.GET.get('year')
    category = get_object_or_404(Category, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)
    units = Unit.objects.filter(id__in=set(category.entries.filter(account__ledgers=ledger).values_list('account__unit', flat=True)))

    if year:
        months = category.entries.filter(Q(account__ledger=ledger) & Q(day__year=year)).dates('day', 'month')
        data = {}
        data['xAxis'] = {'categories':[m.strftime('%B') for m in months], 'title':'months'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')}, 'labels':{'format':'{value}%s' % (units[0].symbol if units.count() == 1 else '')}}
        data['tooltip'] = {'valueSuffix':(units[0].symbol if units.count() == 1 else '')}

        series = []
        for account in Account.objects.filter(Q(entries__category=category) & Q(ledgers=ledger) & Q(entries__day__year=year)).distinct():
            series.append({'name':account.name.lower(), 'data':[[m.strftime('%B'), category.entries.filter(Q(account=account) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months], 'tooltip':{'valueSuffix':account.unit.symbol}, 'type':'column', 'stack':account.unit.name.lower()})

        for unit in units:
            avg = category.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit) & Q(day__year=year)).aggregate(sum=Sum('amount'))['sum'] / len(months)
            series.append({'name':'average %s' % unit.name.lower(), 'type':'spline', 'data':[avg for m in months], 'tooltip':{'valueSuffix':unit.symbol}})
        data['series'] = series
    else:
        years = category.entries.filter(account__ledger=ledger).dates('day', 'year')
        data = {}
        data['xAxis'] = {'categories':[y.strftime('%Y') for y in years], 'title':'years'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')}, 'labels':{'format':'{value}%s' % (units[0].symbol if units.count() == 1 else '')}}
        data['tooltip'] = {'valueSuffix':(units[0].symbol if units.count() == 1 else '')}

        series = []

        for account in Account.objects.filter(Q(entries__category=category) & Q(ledgers=ledger)).distinct():
            series.append({'name':account.name.lower(), 'data':[[y.strftime('%Y'), category.entries.filter(Q(account=account) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years], 'tooltip':{'valueSuffix':account.unit.symbol}, 'type':'column', 'stack':account.unit.name.lower()})

        for unit in units:
            avg = category.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit)).aggregate(sum=Sum('amount'))['sum'] / len(years)
            series.append({'name':'average %s' % unit.name.lower(), 'type':'spline', 'data':[avg for y in years], 'tooltip':{'valueSuffix':unit.symbol}})

        data['series'] = series

    mimetype = 'application/json'
    return HttpResponse(dumps(data), mimetype)
