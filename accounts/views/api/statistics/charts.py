from app.models import Ledger
from accounts.models import Category, Entry, Tag, Unit
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from json import dumps

@login_required(login_url='/login/')
def categories(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    ledger = get_object_or_404(Ledger, user=request.user)
    unit = get_object_or_404(Unit, slug=request.GET.get('unit'))

    data = None
    if month and year:
        days = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year) & Q(day__month=month)).dates('day', 'day')
        data = {}
        data['xAxis'] = {'categories':['%s.' % d.strftime('%d') for d in days], 'title':'days'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % unit.symbol}, 'labels':{'format':'{value}%s' % unit.symbol}}
        data['tooltip'] = {'valueSuffix':unit.symbol}

        series = []
        for category in Category.objects.exclude(account__in=ledger.accounts.all()).filter(Q(entry__account__in=ledger.accounts.all()) & Q(entry__account__unit=unit) & Q(entry__day__year=year) & Q(entry__day__month=month)).distinct():
                series.append({'name':category.name.lower(), 'data':[['%s.' % d.strftime('%d'), category.entry_set.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]})
        data['series'] = series
    elif year:
        months = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year)).dates('day', 'month')
        data = {}
        data['xAxis'] = {'categories':[m.strftime('%B') for m in months], 'title':'months'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % unit.symbol}, 'labels':{'format':'{value}%s' % unit.symbol}}
        data['tooltip'] = {'valueSuffix':unit.symbol}

        series = []
        for category in Category.objects.exclude(account__in=ledger.accounts.all()).filter(Q(entry__account__in=ledger.accounts.all()) & Q(entry__account__unit=unit) & Q(entry__day__year=year)).distinct():
                series.append({'name':category.name.lower(), 'data':[[m.strftime('%B'), category.entry_set.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]})
        data['series'] = series
    else:
        years = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).dates('day', 'year')
        data = {}
        data['xAxis'] = {'categories':[y.strftime('%Y') for y in years], 'title':'years'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % unit.symbol}, 'labels':{'format':'{value}%s' % unit.symbol}}
        data['tooltip'] = {'valueSuffix':unit.symbol}

        series = []
        for category in Category.objects.exclude(account__in=ledger.accounts.all()).filter(Q(entry__account__in=ledger.accounts.all()) & Q(entry__account__unit=unit)).distinct():
                series.append({'name':category.name.lower(), 'data':[[y.strftime('%Y'), category.entry_set.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years]})
        data['series'] = series

    mimetype = 'application/json'
    return HttpResponse(dumps(data), mimetype)

@login_required(login_url='/login/')
def tags(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    ledger = get_object_or_404(Ledger, user=request.user)
    unit = get_object_or_404(Unit, slug=request.GET.get('unit'))

    data = None
    if month and year:
        days = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(tags__isnull=False) & Q(day__year=year) & Q(day__month=month)).dates('day', 'day')
        data = {}
        data['xAxis'] = {'categories':['%s.' % d.strftime('%d') for d in days], 'title':'days'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % unit.symbol}, 'labels':{'format':'{value}%s' % unit.symbol}}
        data['tooltip'] = {'valueSuffix':unit.symbol}

        series = []
        for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct():
            series.append({'name':tag.name.lower(), 'data':[['%s.' % d.strftime('%d'), tag.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in daysp]})
        data['series'] = series
    elif year:
        months = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(tags__isnull=False) & Q(day__year=year)).dates('day', 'month')
        data = {}
        data['xAxis'] = {'categories':[m.strftime('%B') for m in months], 'title':'months'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % unit.symbol}, 'labels':{'format':'{value}%s' % unit.symbol}}
        data['tooltip'] = {'valueSuffix':unit.symbol}

        series = []
        for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year)).distinct():
            series.append({'name':tag.name.lower(), 'data':[[m.strftime('%B'), tag.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]})
        data['series'] = series
    else:
        years = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(tags__isnull=False)).dates('day', 'year')
        data = {}
        data['xAxis'] = {'categories':[y.strftime('%Y') for y in years], 'title':'years'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % unit.symbol}, 'labels':{'format':'{value}%s' % unit.symbol}}
        data['tooltip'] = {'valueSuffix':unit.symbol}

        series = []
        for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit)).distinct():
            series.append({'name':tag.name.lower(), 'data':[[y.strftime('%Y'), tag.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years]})
        data['series'] = series

    mimetype = 'application/json'
    return HttpResponse(dumps(data), mimetype)