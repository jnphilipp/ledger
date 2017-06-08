# -*- coding: utf-8 -*-

import json

from accounts.models import Account
from categories.models import Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


@login_required
def tags(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = {
        'xAxis': {
            'categories': [tag.name.lower() for tag in Tag.objects.filter(id__in=account.entries.values_list('tags', flat=True)).distinct()]
        },
        'series': [{
            'name': 'entries',
            'data': [[tag.name.lower(), tag.count] for tag in Tag.objects.filter(id__in=account.entries.values_list('tags', flat=True)).extra(select={'count':'SELECT COUNT(*) FROM accounts_entry JOIN accounts_entry_tags ON accounts_entry.id=accounts_entry_tags.entry_id WHERE accounts_entry_tags.tag_id=categories_tag.id AND accounts_entry.account_id=%s'}, select_params=(account.id,)).distinct()]
        }]
    }
    return HttpResponse(json.dumps(data), 'application/json')


@login_required
def statistics(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)
    year = request.GET.get('year')
    month = request.GET.get('month')
    t = request.GET.get('tag')

    data = None
    if t and month and year:
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month) & Q(tags__slug=t)).dates('day', 'day')

        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days],
                'title': 'days'
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                }
            },
            'tooltip': {
                'valueSuffix':account.unit.symbol
            },
            'series': [{
                'name': tag.name.lower(),
                'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]
            } for tag in Tag.objects.filter(slug=t).distinct()]
        }
    elif month and year:
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month)).dates('day', 'day')

        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days],
                'title': 'days'
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': tag.name.lower(),
                'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]
            } for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
        }
    elif year:
        months = account.entries.filter(day__year=year).dates('day', 'month')

        data = {
            'xAxis': {
                'categories': [m.strftime('%B') for m in months],
                'title': 'months'
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': tag.name.lower(),
                'data': [[m.strftime('%B'), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]
            } for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year)).distinct()]
        }
    else:
        years = account.entries.dates('day', 'year')

        data = {
            'xAxis': {
                'categories': [y.strftime('%Y') for y in years],
                'title': 'years'
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': tag.name.lower(),
                'data': [[y.strftime('%Y'), account.entries.filter(Q(tags=tag) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years]
            } for tag in Tag.objects.filter(entries__account=account).distinct()]
        }
    return HttpResponse(json.dumps(data), 'application/json')
