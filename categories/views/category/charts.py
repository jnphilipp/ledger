# -*- coding: utf-8 -*-

from accounts.models import Account
from categories.models import Category
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from units.models import Unit
from users.models import Ledger


@login_required
def statistics(request, slug):
    year = request.GET.get('year')
    category = get_object_or_404(Category, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)

    units = set(category.entries.filter(account__ledgers=ledger).
                values_list('account__unit', flat=True))
    units = Unit.objects.filter(id__in=units)
    symbol = units[0].symbol if units.count() == 1 else ''

    if year:
        months = category.entries.filter(Q(account__ledger=ledger) &
                                         Q(day__year=year)).dates('day',
                                                                  'month')
        data = {
            'xAxis': {
                'categories': [m.strftime('%B') for m in months],
                'title': {
                    'text': str(_('Months'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % symbol
                },
                'labels': {
                    'format': '{value}%s' % symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': symbol
            }
        }

        series = []
        accounts = Account.objects.filter(Q(entries__category=category) &
                                          Q(entries__day__year=year) &
                                          Q(ledgers=ledger)).distinct()
        for account in accounts:
            entries = category.entries.filter(Q(account=account) &
                                              Q(day__year=year))
            sdata = []
            for m in months:
                y = entries.filter(day__month=m.strftime('%m')). \
                    aggregate(sum=Sum('amount'))['sum']
                sdata.append((m.strftime('%B'), y))
            series.append({
                'name': account.name,
                'data': sdata,
                'tooltip': {
                    'valueSuffix': account.unit.symbol
                },
                'type': 'column',
                'stack': account.unit.name
            })

        for unit in units:
            amount = category.entries.filter(Q(account__ledgers=ledger) &
                                             Q(account__unit=unit) &
                                             Q(day__year=year)). \
                aggregate(sum=Sum('amount'))
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
        years = category.entries.filter(account__ledger=ledger).dates('day',
                                                                      'year')
        data = {
            'xAxis': {
                'categories': [y.strftime('%Y') for y in years],
                'title': {
                    'text': str(_('Years'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % symbol
                },
                'labels': {
                    'format': '{value}%s' % symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': symbol
            }
        }

        series = []
        accounts = Account.objects.filter(Q(entries__category=category) &
                                          Q(ledgers=ledger)).distinct()
        for account in accounts:
            entries = category.entries.filter(account=account)
            sdata = []
            for y in years:
                v = entries.filter(day__year=y.strftime('%Y')). \
                    aggregate(sum=Sum('amount'))['sum']
                sdata.append((y.strftime('%Y'), v))
            series.append({
                'name': account.name,
                'data': sdata,
                'tooltip': {
                    'valueSuffix': account.unit.symbol
                },
                'type': 'column',
                'stack': account.unit.name
            })

        for unit in units:
            avg = category.entries.filter(Q(account__ledgers=ledger) &
                                          Q(account__unit=unit)
                ).aggregate(sum=Sum('amount'))['sum'] / len(years)
            series.append({
                'name': _('Average %(unit)s') % {'unit': unit.name},
                'type': 'spline',
                'data': [avg for y in years],
                'tooltip': {
                    'valueSuffix': unit.symbol
                }
            })
        data['series'] = series
    return JsonResponse(data)
