# -*- coding: utf-8 -*-

from accounts.models import Entry
from categories.models import Category, Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from json import dumps
from units.models import Unit
from users.models import Ledger


@login_required
def categories(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    ledger = get_object_or_404(Ledger, user=request.user)
    unit = get_object_or_404(Unit, slug=request.GET.get('unit'))

    data = None
    if month and year:
        days = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year) & Q(day__month=month)).dates('day', 'day')
        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days],
                'title': {
                    'text': str(_('Days'))
                }
            },
            'yAxis': {
                'stackLabels': {'format': '{total:,.2f}%s' % unit.symbol},
                'labels': {'format': '{value}%s' % unit.symbol},
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {'valueSuffix': unit.symbol}
        }

        series = []
        for category in Category.objects.exclude(accounts__in=ledger.accounts.all()).filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct():
                series.append({
                    'name': category.name,
                    'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')), category.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]})
        data['series'] = series
    elif year:
        months = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(day__year=year)).dates('day', 'month')
        data = {
            'xAxis': {
                'categories': [m.strftime('%B') for m in months],
                'title': {
                    'text': str(_('Months'))
                }
            },
            'yAxis': {
                'stackLabels': {'format': '{total:,.2f}%s' % unit.symbol},
                'labels': {'format': '{value}%s' % unit.symbol},
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {'valueSuffix': unit.symbol}
        }

        series = []
        for category in Category.objects.exclude(accounts__in=ledger.accounts.all()).filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year)).distinct():
                series.append({
                    'name': category.name,
                    'data': [[m.strftime('%B'), category.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]})
        data['series'] = series
    else:
        years = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).dates('day', 'year')
        data = {
            'xAxis': {
                'categories': [y.strftime('%Y') for y in years],
                'title': {
                    'text': str(_('Years'))
                }
            },
            'yAxis': {
                'stackLabels': {'format': '{total:,.2f}%s' % unit.symbol},
                'labels': {'format': '{value}%s' % unit.symbol},
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {'valueSuffix': unit.symbol}
        }

        series = []
        for category in Category.objects.exclude(accounts__in=ledger.accounts.all()).filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit)).distinct():
                series.append({
                    'name': category.name,
                    'data': [[y.strftime('%Y'), category.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years]})
        data['series'] = series
    return HttpResponse(dumps(data), 'application/json')


@login_required
def tags(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    ledger = get_object_or_404(Ledger, user=request.user)
    unit = get_object_or_404(Unit, slug=request.GET.get('unit'))

    data = None
    if month and year:
        days = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(tags__isnull=False) & Q(day__year=year) & Q(day__month=month)).dates('day', 'day')
        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days],
                'title': {
                    'text': str(_('Days'))
                }
            },
            'yAxis': {
                'stackLabels': {'format': '{total:,.2f}%s' % unit.symbol},
                'labels': {'format': '{value}%s' % unit.symbol},
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {'valueSuffix': unit.symbol}
        }

        series = []
        for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct():
            series.append({
                'name': tag.name,
                'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')), tag.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]})
        data['series'] = series
    elif year:
        months = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(tags__isnull=False) & Q(day__year=year)).dates('day', 'month')
        data = {
            'xAxis': {
                'categories': [m.strftime('%B') for m in months],
                'title': {
                    'text': str(_('Months'))
                }
            },
            'yAxis': {
                'stackLabels': {'format': '{total:,.2f}%s' % unit.symbol},
                'labels': {'format': '{value}%s' % unit.symbol},
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {'valueSuffix': unit.symbol}
        }

        series = []
        for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit) & Q(entries__day__year=year)).distinct():
            series.append({
                'name': tag.name,
                'data': [[m.strftime('%B'), tag.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]})
        data['series'] = series
    else:
        years = Entry.objects.filter(Q(account__in=ledger.accounts.filter(unit=unit)) & Q(tags__isnull=False)).dates('day', 'year')
        data = {
            'xAxis': {
                'categories': [y.strftime('%Y') for y in years],
                'title': {
                    'text': str(_('Years'))
                }
            },
            'yAxis': {
                'stackLabels': {'format': '{total:,.2f}%s' % unit.symbol},
                'labels': {'format': '{value}%s' % unit.symbol},
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {'valueSuffix': unit.symbol}
        }

        series = []
        for tag in Tag.objects.filter(Q(entries__account__in=ledger.accounts.all()) & Q(entries__account__unit=unit)).distinct():
            series.append({
                'name': tag.name,
                'data': [[y.strftime('%Y'), tag.entries.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years]})
        data['series'] = series
    return HttpResponse(dumps(data), 'application/json')
