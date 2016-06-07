# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from categories.models import Category, Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from json import dumps


@login_required(login_url='/users/signin/')
def categories(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)
    year = request.GET.get('year')
    month = request.GET.get('month')
    c = request.GET.get('category')

    data = None
    if c and month and year:
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month) & Q(category__slug=c)).dates('day', 'day')
        data = {}
        data['xAxis'] = {'categories':['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days], 'title':'days'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for category in Category.objects.filter(slug=c).distinct():
            series.append({'name':category.name.lower(), 'data':[['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(category=category) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]})
        data['series'] = series
    elif month and year:
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month)).dates('day', 'day')
        data = {}
        data['xAxis'] = {'categories':['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days], 'title':'days'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for category in Category.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct():
            series.append({'name':category.name.lower(), 'data':[['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(category=category) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]})
        data['series'] = series
    elif year:
        months = account.entries.filter(day__year=year).dates('day', 'month')
        data = {}
        data['xAxis'] = {'categories':[m.strftime('%B') for m in months], 'title':'months'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for category in Category.objects.filter(Q(entries__account=account) & Q(entries__day__year=year)).distinct():
            series.append({'name':category.name.lower(), 'data':[[m.strftime('%B'), account.entries.filter(Q(category=category) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]})
        data['series'] = series
    else:
        years = account.entries.dates('day', 'year')
        data = {}
        data['xAxis'] = {'categories':[y.strftime('%Y') for y in years], 'title':'years'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for category in Category.objects.filter(entries__account=account).distinct():
            series.append({'name':category.name.lower(), 'data':[[y.strftime('%Y'), account.entries.filter(Q(category=category) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years]})
        data['series'] = series
    return HttpResponse(dumps(data), 'application/json')


@login_required(login_url='/users/signin/')
def tags(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)
    year = request.GET.get('year')
    month = request.GET.get('month')
    t = request.GET.get('tag')

    data = None
    if t and month and year:
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month) & Q(tags__slug=t)).dates('day', 'day')
        data = {}
        data['xAxis'] = {'categories':['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days], 'title':'days'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for tag in Tag.objects.filter(slug=t).distinct():
            series.append({'name':tag.name.lower(), 'data':[['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]})
        data['series'] = series
    elif month and year:
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month)).dates('day', 'day')
        data = {}
        data['xAxis'] = {'categories':['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days], 'title':'days'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct():
            series.append({'name':tag.name.lower(), 'data':[['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]})
        data['series'] = series
    elif year:
        months = account.entries.filter(day__year=year).dates('day', 'month')
        data = {}
        data['xAxis'] = {'categories':[m.strftime('%B') for m in months], 'title':'months'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year)).distinct():
            series.append({'name':tag.name.lower(), 'data':[[m.strftime('%B'), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]})
        data['series'] = series
    else:
        years = account.entries.dates('day', 'year')
        data = {}
        data['xAxis'] = {'categories':[y.strftime('%Y') for y in years], 'title':'years'}
        data['yAxis'] = {'stackLabels':{'format':'{total:,.2f}%s' % account.unit.symbol}, 'labels':{'format':'{value}%s' % account.unit.symbol}}
        data['tooltip'] = {'valueSuffix':account.unit.symbol}

        series = []
        for tag in Tag.objects.filter(entries__account=account).distinct():
            series.append({'name':tag.name.lower(), 'data':[[y.strftime('%Y'), account.entries.filter(Q(tags=tag) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years]})
        data['series'] = series
    return HttpResponse(dumps(data), 'application/json')
