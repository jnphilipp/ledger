# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from categories.models import Category, Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _


@login_required
def categories(request, slug, year=None, month=None, category=None):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = None
    if category and month and year:
        c = get_object_or_404(Category, slug=category)
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month) &
                                      Q(category=c)).dates('day', 'day')
        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'),
                                           d.strftime('%B')) for d in days],
                'title': {
                    'text': str(_('Days'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': c.name,
                'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')),
                          account.entries.filter(Q(category=c) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]
            }]
        }
    elif month and year:
        days = account.entries.filter(Q(day__year=year) &
                                      Q(day__month=month)).dates('day', 'day')
        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'),
                                           d.strftime('%B')) for d in days],
                'title': {
                    'text': str(_('Days'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': c.name,
                'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(category=c) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]
            } for c in Category.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
        }
    elif year:
        months = account.entries.filter(day__year=year).dates('day', 'month')
        data = {
            'xAxis': {
                'categories': [m.strftime('%B') for m in months],
                'title': {
                    'text': str(_('Months'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': c.name,
                'data': [[m.strftime('%B'),
                          account.entries.filter(Q(category=c) &
                                                 Q(day__year=year) &
                                                 Q(day__month=m.strftime('%m'))
                          ).aggregate(sum=Sum('amount'))['sum']] for m in months]
            } for c in Category.objects.filter(Q(entries__account=account) & Q(entries__day__year=year)).distinct()]
        }
    else:
        years = account.entries.dates('day', 'year')
        data = {
            'xAxis': {
                'categories': [y.strftime('%Y') for y in years],
                'title': {
                    'text': str(_('Years'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': c.name,
                'data': [[y.strftime('%Y'),
                          account.entries.filter(Q(category=c) &
                                                 Q(day__year=y.strftime('%Y'))
                          ).aggregate(sum=Sum('amount'))['sum']]
                         for y in years]
            } for c in Category.objects.filter(entries__account=account). \
                distinct()]
        }
    return JsonResponse(data)


@login_required
def tags(request, slug, year=None, month=None, tag=None):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = None
    if tag and month and year:
        t = get_object_or_404(Tag, slug=tag)
        days = account.entries.filter(Q(day__year=year) & Q(day__month=month) &
                                      Q(tags=t)).dates('day', 'day')
        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'),
                                           d.strftime('%B')) for d in days],
                'title': {
                    'text': str(_('Days'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': t.name,
                'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(tags=t) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]
            }]
        }
    elif month and year:
        days = account.entries.filter(Q(day__year=year) &
                                      Q(day__month=month)).dates('day', 'day')
        data = {
            'xAxis': {
                'categories': ['%s. %s' % (d.strftime('%d'), d.strftime('%B')) for d in days],
                'title': {
                    'text': str(_('Days'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': tag.name,
                'data': [['%s. %s' % (d.strftime('%d'), d.strftime('%B')), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=month) & Q(day__day=d.strftime('%d'))).aggregate(sum=Sum('amount'))['sum']] for d in days]
            } for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
        }
    elif year:
        months = account.entries.filter(day__year=year).dates('day', 'month')
        data = {
            'xAxis': {
                'categories': [m.strftime('%B') for m in months],
                'title': {
                    'text': str(_('Months'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix': account.unit.symbol
            },
            'series': [{
                'name': tag.name,
                'data': [[m.strftime('%B'), account.entries.filter(Q(tags=tag) & Q(day__year=year) & Q(day__month=m.strftime('%m'))).aggregate(sum=Sum('amount'))['sum']] for m in months]
            } for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year)).distinct()]
        }
    else:
        years = account.entries.dates('day', 'year')
        data = {
            'xAxis': {
                'categories': [y.strftime('%Y') for y in years],
                'title': {
                    'text': str(_('Years'))
                }
            },
            'yAxis': {
                'stackLabels': {
                    'format': '{total:,.2f}%s' % account.unit.symbol
                },
                'labels': {
                    'format': '{value}%s' % account.unit.symbol
                },
                'title': {
                    'text': str(_('Loss and Profit'))
                }
            },
            'tooltip': {
                'valueSuffix':account.unit.symbol
            },
            'series': [{
                'name': t.name,
                'data': [[y.strftime('%Y'),
                          account.entries.filter(Q(tags=t) &
                                                 Q(day__year=y.strftime('%Y'))
                                                ).aggregate(sum=Sum('amount'))['sum']] for y in years]
            } for t in Tag.objects.filter(entries__account=account).distinct()]
        }
    return JsonResponse(data)
