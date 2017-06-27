# -*- coding: utf-8 -*-

import json

from accounts.models import Account
from categories.models import Category
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from units.models import Unit
from users.models import Ledger


@login_required
def statistics(request, slug):
    year = request.GET.get('year')
    category = get_object_or_404(Category, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)
    units = Unit.objects.filter(id__in=set(category.entries.filter(account__ledgers=ledger).values_list('account__unit', flat=True)))

    if year:
        months = category.entries.filter(Q(account__ledger=ledger) & Q(day__year=year)).dates('day', 'month')
        data = {
            'xAxis': {
                'categories': [m.strftime('%B') for m in months],
                'title': {
                    'text': str(_('Months'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')
                },
                'labels': {
                    'format': '{value}%s' % (units[0].symbol if units.count() == 1 else '')
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': (units[0].symbol if units.count() == 1 else '')
            }
        }

        series = []
        for account in Account.objects.filter(Q(entries__category=category) & Q(ledgers=ledger) & Q(entries__day__year=year)).distinct():
            series.append({
                'name': account.name,
                'data': [[m.strftime('%B'), category.entries.filter(Q(account=account) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months],
                'tooltip': {
                    'valueSuffix': account.unit.symbol
                },
                'type': 'column',
                'stack': account.unit.name
            })

        for unit in units:
            amount = category.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit) & Q(day__year=year)).aggregate(sum=Sum('amount'))
            if amount['sum']:
                avg = amount['sum'] / len(months)
                series.append({
                    'name': _('Average %(unit)s') % {'unit': unit.name},
                    'type': 'spline',
                    'data': [avg for m in months],
                    'tooltip': {
                        'valueSuffix': unit.symbol
                    }
                })
        data['series'] = series
    else:
        years = category.entries.filter(account__ledger=ledger).dates('day', 'year')
        data = {
            'xAxis': {
                'categories': [y.strftime('%Y') for y in years],
                'title': {
                    'text': str(_('Years'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % (units[0].symbol if units.count() == 1 else '')
                },
                'labels': {
                    'format': '{value}%s' % (units[0].symbol if units.count() == 1 else '')
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': (units[0].symbol if units.count() == 1 else '')
            }
        }

        series = []
        for account in Account.objects.filter(Q(entries__category=category) & Q(ledgers=ledger)).distinct():
            series.append({
                'name': account.name,
                'data': [[y.strftime('%Y'), category.entries.filter(Q(account=account) & Q(day__year=y.strftime('%Y'))).aggregate(sum=Sum('amount'))['sum']] for y in years],
                'tooltip': {
                    'valueSuffix': account.unit.symbol
                },
                'type': 'column',
                'stack': account.unit.name
            })

        for unit in units:
            avg = category.entries.filter(Q(account__ledgers=ledger) & Q(account__unit=unit)).aggregate(sum=Sum('amount'))['sum'] / len(years)
            series.append({
                'name': _('Average %(unit)s') % {'unit': unit.name},
                'type': 'spline',
                'data': [avg for y in years],
                'tooltip': {
                    'valueSuffix': unit.symbol
                }
            })
        data['series'] = series
    return HttpResponse(json.dumps(data), 'application/json')
