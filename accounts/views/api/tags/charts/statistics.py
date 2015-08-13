from accounts.models import Account, Category, Tag, Unit
from app.models import Ledger
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from json import dumps

@login_required(login_url='/signin/')
def accounts(request, slug):
    year = request.GET.get('year')
    tag = get_object_or_404(Tag, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)
    units = Unit.objects.filter(id__in=set(tag.entries.filter(account__ledgers=ledger).values_list('account__unit', flat=True)))

    if year:
        months = tag.entries.filter(Q(account__ledger=ledger) & Q(day__year=year)).dates('day', 'month')
        data = {}
        data['xAxis'] = {'categories':[m.strftime('%B') for m in months], 'title':'months'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')}, 'labels':{'format':'{value}%s' % (units[0].symbol if units.count() == 1 else '')}}
        data['tooltip'] = {'valueSuffix':(units[0].symbol if units.count() == 1 else '')}

        series = []
        for account in Account.objects.filter(Q(entries__tags=tag) & Q(ledgers=ledger) & Q(entries__day__year=year)).distinct():
            series.append({'name':account.name.lower(), 'data':[[m.strftime('%B'), tag.entries.filter(Q(account=account) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months], 'tooltip':{'valueSuffix':account.unit.symbol}, 'type':'column', 'stack':account.unit.name.lower()})

        for unit in units:
            avg = tag.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit) & Q(day__year=year)).aggregate(sum=Sum('amount'))['sum'] / len(months)
            series.append({'name':'average %s' % unit.name.lower(), 'type':'spline', 'data':[avg for m in months], 'tooltip':{'valueSuffix':unit.symbol}})
        data['series'] = series
    else:
        years = tag.entries.filter(account__ledger=ledger).dates('day', 'year')
        data = {}
        data['xAxis'] = {'categories':[y.strftime('%Y') for y in years], 'title':'years'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')}, 'labels':{'format':'{value}%s' % (units[0].symbol if units.count() == 1 else '')}}
        data['tooltip'] = {'valueSuffix':(units[0].symbol if units.count() == 1 else '')}

        series = []

        for account in Account.objects.filter(Q(entries__tags=tag) & Q(ledgers=ledger)).distinct():
            series.append({'name':account.name.lower(), 'data':[[y.strftime('%Y'), tag.entries.filter(Q(account=account) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years], 'tooltip':{'valueSuffix':account.unit.symbol}, 'type':'column', 'stack':account.unit.name.lower()})

        for unit in units:
            avg = tag.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit)).aggregate(sum=Sum('amount'))['sum'] / len(years)
            series.append({'name':'average %s' % unit.name.lower(), 'type':'spline', 'data':[avg for y in years], 'tooltip':{'valueSuffix':unit.symbol}})

        data['series'] = series
    return HttpResponse(dumps(data), 'application/json')

@login_required(login_url='/signin/')
def categories(request, slug):
    year = request.GET.get('year')
    tag = get_object_or_404(Tag, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)
    units = Unit.objects.filter(id__in=set(tag.entries.filter(account__ledgers=ledger).values_list('account__unit', flat=True)))

    if year:
        months = tag.entries.filter(Q(account__ledger=ledger) & Q(day__year=year)).dates('day', 'month')
        data = {}
        data['xAxis'] = {'categories':[m.strftime('%B') for m in months], 'title':'months'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')}, 'labels':{'format':'{value}%s' % (units[0].symbol if units.count() == 1 else '')}}
        data['tooltip'] = {'valueSuffix':(units[0].symbol if units.count() == 1 else '')}

        series = []
        for category in Category.objects.filter(Q(entries__tags=tag) & Q(entries__account__ledgers=ledger) & Q(entries__day__year=year)).distinct():
            for unit in units:
                series.append({'name':category.name.lower(), 'data':[[m.strftime('%B'), tag.entries.filter(Q(category=category) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months], 'tooltip':{'valueSuffix':unit.symbol}, 'type':'column', 'stack':unit.name.lower()})

        for unit in units:
            avg = tag.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit) & Q(day__year=year)).aggregate(sum=Sum('amount'))['sum'] / len(months)
            series.append({'name':'average %s' % unit.name.lower(), 'type':'spline', 'data':[avg for m in months], 'tooltip':{'valueSuffix':unit.symbol}})
        data['series'] = series
    else:
        years = tag.entries.filter(account__ledger=ledger).dates('day', 'year')
        data = {}
        data['xAxis'] = {'categories':[y.strftime('%Y') for y in years], 'title':'years'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')}, 'labels':{'format':'{value}%s' % (units[0].symbol if units.count() == 1 else '')}}
        data['tooltip'] = {'valueSuffix':(units[0].symbol if units.count() == 1 else '')}

        series = []

        for category in Category.objects.filter(Q(entries__tags=tag) & Q(entries__account__ledgers=ledger)).distinct():
            for unit in units:
                series.append({'name':category.name.lower(), 'data':[[y.strftime('%Y'), tag.entries.filter(Q(category=category) & Q(account__unit=unit) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years], 'tooltip':{'valueSuffix':unit.symbol}, 'type':'column', 'stack':unit.name.lower()})

        for unit in units:
            avg = tag.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit)).aggregate(sum=Sum('amount'))['sum'] / len(years)
            series.append({'name':'average %s' % unit.name.lower(), 'type':'spline', 'data':[avg for y in years], 'tooltip':{'valueSuffix':unit.symbol}})

        data['series'] = series
    return HttpResponse(dumps(data), 'application/json')
