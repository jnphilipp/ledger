# -*- coding: utf-8 -*-

import json

from accounts.models import Entry
from accounts.templatetags.accounts import colorfy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from units.models import Unit
from users.forms import BudgetForm
from users.models import Budget, Ledger


@login_required
def budget(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    budget = get_object_or_404(Budget, user=request.user)

    unit_slug = request.GET.get('unit')
    year = request.GET.get('year')
    years = [y.strftime('%Y') for y in Entry.objects.filter(account__in=ledger.accounts.all()).dates('day', 'year')]
    if not year:
        y = str(timezone.now().year)
        year = y if y in years else years[-1]
    if year:
        units = set()
        series = {}
        drilldown = {}

        footer = []
        footer.append(_('Sum'))
        footer.append({})
        footer.append({})

        income = []
        for tag in budget.income_tags.all():
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('account__unit', 'amount'):
                amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                income.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown:
                    drilldown[unit] = {}
                if 'income' not in drilldown[unit]:
                    drilldown[unit]['income'] = {
                        'name': str(_('Income')),
                        'id': 'income',
                        'dataLabels': {
                            'enabled': True,
                            'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                        },
                        'tooltip': {
                            'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                            'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                        },
                        'data': []
                    }
                drilldown[unit]['income']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': tag.name
                })
            drilldown[unit][tag.name] = {
                'name': tag.name,
                'id': tag.name,
                'dataLabels': {
                    'enabled': True,
                    'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                },
                'tooltip': {
                    'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                    'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                },
                'data': []
            }
            categories = {}
            for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                if entry.category.name in categories:
                    categories[entry.category.name]['y'] += entry.amount
                else:
                    categories[entry.category.name] = {
                        'name': entry.category.name,
                        'y': entry.amount
                    }
            for k, v in categories.items():
                categories[k]['y'] = abs(v['y'])
            drilldown[unit][tag.name]['data'] = [v for k, v in categories.items()]
            for k, v in amounts.items():
                footer[1][k] = footer[1][k] + (v / 12) if k in footer[1] else (v / 12)
                footer[2][k] = footer[2][k] + v if k in footer[2] else v
        units.update(footer[1].keys())
        for unit in units:
            series[unit] = {
                'name': str(_('Budget %(unit)s' % {'unit': unit.name}) if len(units) > 1 else _('Budget')),
                'colorByPoint': True,
                'dataLabels': {
                    'enabled': True,
                    'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                },
                'tooltip': {
                    'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                    'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                },
                'data': [{
                    'name': str(_('Income')),
                    'y': abs(footer[2][unit]),
                    'drilldown': 'income'
                }]
            }

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        consumption = []
        for tag in budget.consumption_tags.all():
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('account__unit', 'amount'):
                amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                consumption.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown:
                    drilldown[unit] = {}
                if 'consumption' not in drilldown[unit]:
                    drilldown[unit]['consumption'] = {
                        'name': str(_('Consumption')),
                        'id': 'consumption',
                        'dataLabels': {
                            'enabled': True,
                            'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                        },
                        'tooltip': {
                            'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                            'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                        },
                        'data': []
                    }
                drilldown[unit]['consumption']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': tag.name
                })
            drilldown[unit][tag.name] = {
                'name': tag.name,
                'id': tag.name,
                'dataLabels': {
                    'enabled': True,
                    'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                },
                'tooltip': {
                    'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                    'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                },
                'data': []
            }
            categories = {}
            for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                if entry.category.name in categories:
                    categories[entry.category.name]['y'] += entry.amount
                else:
                    categories[entry.category.name] = {
                        'name': entry.category.name,
                        'y': entry.amount
                    }
            for k, v in categories.items():
                categories[k]['y'] = abs(v['y'])
            drilldown[unit][tag.name]['data'] = [v for k, v in categories.items()]
            for k, v in amounts.items():
                footer[4][k] = footer[4][k] + (v / 12) if k in footer[4] else (v / 12)
                footer[5][k] = footer[5][k] + v if k in footer[5] else v
        units.update(footer[4].keys())
        for unit in units:
            if unit in series and unit in footer[5]:
                series[unit]['data'].append({
                    'name': str(_('Consumption')),
                    'y': abs(footer[5][unit]),
                    'drilldown': 'consumption'
                })
            elif unit in footer[5]:
                series[unit] = {
                    'name': str(_('Budget %(unit)s' % {'unit': unit.name})),
                    'colorByPoint': True,
                    'dataLabels': {
                        'enabled': True,
                        'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                    },
                    'tooltip': {
                        'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                        'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                    },
                    'data': [{
                        'name': str(_('Consumption')),
                        'y': abs(footer[5][unit]),
                        'drilldown': 'consumption'
                    }]
                }

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        insurance = []
        for tag in budget.insurance_tags.all():
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('account__unit', 'amount'):
                amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                insurance.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown:
                    drilldown[unit] = {}
                if 'insurance' not in drilldown[unit]:
                    drilldown[unit]['insurance'] = {
                        'name': str(_('Insurance')),
                        'id': 'insurance',
                        'dataLabels': {
                            'enabled': True,
                            'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                        },
                        'tooltip': {
                            'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                            'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                        },
                        'data': []
                    }
                drilldown[unit]['insurance']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': tag.name
                })
            drilldown[unit][tag.name] = {
                'name': tag.name,
                'id': tag.name,
                'dataLabels': {
                    'enabled': True,
                    'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                },
                'tooltip': {
                    'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                    'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                },
                'data': []
            }
            categories = {}
            for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                if entry.category.name in categories:
                    categories[entry.category.name]['y'] += entry.amount
                else:
                    categories[entry.category.name] = {
                        'name': entry.category.name,
                        'y': entry.amount
                    }
            for k, v in categories.items():
                categories[k]['y'] = abs(v['y'])
            drilldown[unit][tag.name]['data'] = [v for k, v in categories.items()]
            for k, v in amounts.items():
                footer[7][k] = footer[7][k] + (v / 12) if k in footer[7] else (v / 12)
                footer[8][k] = footer[8][k] + v if k in footer[8] else v
        units.update(footer[7].keys())
        for unit in units:
            if unit in series and unit in footer[8]:
                series[unit]['data'].append({
                    'name': str(_('Insurance')),
                    'y': abs(footer[8][unit]),
                    'drilldown': 'insurance'
                })
            elif unit in footer[8]:
                series[unit] = {
                    'name': str(_('Budget %(unit)s' % {'unit': unit.name})),
                    'colorByPoint': True,
                    'dataLabels': {
                        'enabled': True,
                        'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                    },
                    'tooltip': {
                        'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                        'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                    },
                    'data': [{
                        'name': str(_('Insurance')),
                        'y': abs(footer[8][unit]),
                        'drilldown': 'insurance'
                    }]
                }

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        savings = []
        for tag in budget.savings_tags.all():
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('account__unit', 'amount'):
                amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                savings.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown:
                    drilldown[unit] = {}
                if 'savings' not in drilldown[unit]:
                    drilldown[unit]['savings'] = {
                        'name': str(_('Savings')),
                        'id': 'savings',
                        'dataLabels': {
                            'enabled': True,
                            'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                        },
                        'tooltip': {
                            'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                            'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                        },
                        'data': []
                    }
                drilldown[unit]['savings']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': tag.name
                })
            drilldown[unit][tag.name] = {
                'name': tag.name,
                'id': tag.name,
                'dataLabels': {
                    'enabled': True,
                    'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                },
                'tooltip': {
                    'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                    'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                },
                'data': []
            }
            categories = {}
            for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                if entry.category.name in categories:
                    categories[entry.category.name]['y'] += entry.amount
                else:
                    categories[entry.category.name] = {
                        'name': entry.category.name,
                        'y': entry.amount
                    }
            for k, v in categories.items():
                categories[k]['y'] = abs(v['y'])
            drilldown[unit][tag.name]['data'] = [v for k, v in categories.items()]
            for k, v in amounts.items():
                footer[10][k] = footer[10][k] + (v / 12) if k in footer[10] else (v / 12)
                footer[11][k] = footer[11][k] + v if k in footer[11] else v
        units.update(footer[10].keys())
        for unit in units:
            if unit in series and unit in footer[11]:
                series[unit]['data'].append({
                    'name': str(_('Savings')),
                    'y': abs(footer[11][unit]),
                    'drilldown': 'savings'
                })
            elif unit in footer[11]:
                series[unit] = {
                    'name': str(_('Budget %(unit)s' % {'unit': unit.name})),
                    'colorByPoint': True,
                    'dataLabels': {
                        'enabled': True,
                        'format': '{point.name}: {point.y:.%df} %s' % (unit.precision, unit.symbol)
                    },
                    'tooltip': {
                        'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
                        'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
                    },
                    'data': [{
                        'name': str(_('Savings')),
                        'y': abs(footer[11][unit]),
                        'drilldown': 'savings'
                    }]
                }

        footer = [footer.copy() for unit in units]
        for i, unit in enumerate(units):
            if i > 0:
                footer[i][0] = footer[i][3] = footer[i][6] = footer[i][9] = ''

            footer.append(['', '', '', '', '', '', '', '', '', _('Total') if i == 0 else '', 0, 0])
            footer[-1][10] = (footer[i][1][unit] if unit in footer[i][1] else 0) + (footer[i][4][unit] if unit in footer[i][4] else 0) + (footer[i][7][unit] if unit in footer[i][7] else 0) + (footer[i][10][unit] if unit in footer[i][10] else 0)
            footer[-1][11] = (footer[i][2][unit] if unit in footer[i][2] else 0) + (footer[i][5][unit] if unit in footer[i][5] else 0) + (footer[i][8][unit] if unit in footer[i][8] else 0) + (footer[i][11][unit] if unit in footer[i][11] else 0)

            footer[i][1] = colorfy(footer[i][1][unit], unit) if unit in footer[i][1] else ''
            footer[i][2] = colorfy(footer[i][2][unit], unit) if unit in footer[i][2] else ''
            footer[i][4] = colorfy(footer[i][4][unit], unit) if unit in footer[i][4] else ''
            footer[i][5] = colorfy(footer[i][5][unit], unit) if unit in footer[i][5] else ''
            footer[i][7] = colorfy(footer[i][7][unit], unit) if unit in footer[i][7] else ''
            footer[i][8] = colorfy(footer[i][8][unit], unit) if unit in footer[i][8] else ''
            footer[i][10] = colorfy(footer[i][10][unit], unit) if unit in footer[i][10] else ''
            footer[i][11] = colorfy(footer[i][11][unit], unit) if unit in footer[i][11] else ''
            footer[-1][10] = colorfy(footer[-1][10], unit)
            footer[-1][11] = colorfy(footer[-1][11], unit)

        for i, unit in enumerate(units):
            real = Entry.objects.exclude(category__in=ledger.accounts.values_list('category', flat=True)).filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year)).aggregate(sum=Sum('amount'))['sum']
            footer.append(['', '', '', '', '', '', '', '', '', _('Real') if i == 0 else '', 0, 0])
            footer[-1][10] = colorfy(real / 12, unit)
            footer[-1][11] = colorfy(real, unit)

        table = []
        for i in range(max(len(income), len(consumption), len(insurance), len(savings))):
            row = []
            if i < len(income):
                row.append([income[i]['slug'], income[i]['name']] if income[i]['name'] else '')
                row.append(income[i]['monthly'])
                row.append(income[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(consumption):
                row.append([consumption[i]['slug'], consumption[i]['name']] if consumption[i]['name'] else '')
                row.append(consumption[i]['monthly'])
                row.append(consumption[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(insurance):
                row.append([insurance[i]['slug'], insurance[i]['name']] if insurance[i]['name'] else '')
                row.append(insurance[i]['monthly'])
                row.append(insurance[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(savings):
                row.append([savings[i]['slug'], savings[i]['name']] if savings[i]['name'] else '')
                row.append(savings[i]['monthly'])
                row.append(savings[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            table.append(row)
        if len(series) == 1:
            print(series)
            series = json.dumps([v for k, v in series.items()])
            drilldown = json.dumps({'series': [s for k, v in drilldown.items() for k2, s in drilldown[k].items()]})
        else:
            series = dict((k.id, json.dumps([v])) for k, v in series.items())
            drilldown = dict((k.id, json.dumps({'series': [v2 for k2, v2 in v.items()]})) for k, v in drilldown.items())
            print(drilldown)
    return render(request, 'users/budget/budget.html', locals())


@login_required
def edit(request):
    budget = get_object_or_404(Budget, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(instance=budget, data=request.POST)
        if form.is_valid():
            budget = form.save()
            messages.add_message(request, messages.SUCCESS, _('Your budget was successfully updated.'))
            return redirect('users:budget')
        return render(request, 'users/budget/edit.html', locals())
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'users/budget/edit.html', locals())
