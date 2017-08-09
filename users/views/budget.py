# -*- coding: utf-8 -*-

import json

from accounts.models import Entry
from accounts.templatetags.accounts import colorfy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Func, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from units.models import Unit
from users.functions import budget as fbudget
from users.forms import BudgetForm
from users.models import Budget, Ledger


@login_required
def budget(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    budget = get_object_or_404(Budget, user=request.user)

    unit_slug = request.GET.get('unit')
    year = request.GET.get('year')
    years = [y.strftime('%Y') for y in Entry.objects.filter(account__in=ledger.accounts.all()).dates('day', 'year')]
    entry_ids = set()
    if not year:
        y = str(timezone.now().year)
        year = y if y in years else years[-1]
    if year:
        units = set()
        series = [{}, {}]
        drilldown = [{}, {}]

        footer = []
        footer.append(_('Sum'))
        footer.append({})
        footer.append({})

        income = []
        for tag in budget.income_tags.annotate(name_lower=Func(F('name'), function='LOWER')).order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('pk', 'account__unit', 'amount'):
                if e['pk'] not in entry_ids:
                    amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
                    entry_ids.add(e['pk'])
            unit = None
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                income.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'income' not in drilldown[0][unit]:
                    drilldown[0][unit]['income'] = fbudget.make_drilldown(str(_('Income')), 'income', unit)
                    drilldown[1][unit]['income'] = fbudget.make_drilldown(str(_('Income')), 'income', unit)
                drilldown[0][unit]['income']['data'].append({
                    'name': tag.name,
                    'y': abs(v) / 12,
                    'drilldown': 'income_%s' % tag.slug
                })
                drilldown[1][unit]['income']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': 'income_%s' % tag.slug
                })
            if unit:
                drilldown[0][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'income_%s' % tag.slug, unit)
                drilldown[1][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'income_%s' % tag.slug, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                    if entry.category.slug in categories[0]:
                        categories[0][entry.category.slug]['y'] += entry.amount
                        categories[1][entry.category.slug]['y'] += entry.amount
                    else:
                        categories[0][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                        categories[1][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['y']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['y'])
                drilldown[0][unit][tag.slug]['data'] = [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.slug]['data'] = [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                footer[1][k] = footer[1][k] + (v / 12) if k in footer[1] else (v / 12)
                footer[2][k] = footer[2][k] + v if k in footer[2] else v
        units.update(footer[1].keys())
        for unit in units:
            series[0][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name}) if len(units) > 1 else _('Budget')), unit)
            series[1][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name}) if len(units) > 1 else _('Budget')), unit)
            series[0][unit]['data'].append({
                'name': str(_('Income')),
                'y': abs(footer[2][unit]) / 12,
                'drilldown': 'income'
            })
            series[1][unit]['data'].append({
                'name': str(_('Income')),
                'y': abs(footer[2][unit]),
                'drilldown': 'income'
            })

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        consumption = []
        for tag in budget.consumption_tags.annotate(name_lower=Func(F('name'), function='LOWER')).order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('pk', 'account__unit', 'amount'):
                if e['pk'] not in entry_ids:
                    amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
                    entry_ids.add(e['pk'])
            unit = None
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                consumption.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'consumption' not in drilldown[0][unit]:
                    drilldown[0][unit]['consumption'] = fbudget.make_drilldown(str(_('Consumption')), 'consumption', unit)
                    drilldown[1][unit]['consumption'] = fbudget.make_drilldown(str(_('Consumption')), 'consumption', unit)
                drilldown[0][unit]['consumption']['data'].append({
                    'name': tag.name,
                    'y': abs(v) / 12,
                    'drilldown': 'consumption_%s' % tag.slug
                })
                drilldown[1][unit]['consumption']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': 'consumption_%s' % tag.slug
                })
            if unit:
                drilldown[0][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'consumption_%s' % tag.slug, unit)
                drilldown[1][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'consumption_%s' % tag.slug, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                    if entry.category.slug in categories[0]:
                        categories[0][entry.category.slug]['y'] += entry.amount
                        categories[1][entry.category.slug]['y'] += entry.amount
                    else:
                        categories[0][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                        categories[1][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['y']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['y'])
                drilldown[0][unit][tag.slug]['data'] = [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.slug]['data'] = [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                footer[4][k] = footer[4][k] + (v / 12) if k in footer[4] else (v / 12)
                footer[5][k] = footer[5][k] + v if k in footer[5] else v
        units.update(footer[4].keys())
        for unit in units:
            if unit not in series[0] and unit in footer[5]:
                series[0][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name})), unit)
                series[1][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name})), unit)
            if unit in footer[5]:
                series[0][unit]['data'].append({
                    'name': str(_('Consumption')),
                    'y': abs(footer[5][unit]) / 12,
                    'drilldown': 'consumption'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Consumption')),
                    'y': abs(footer[5][unit]),
                    'drilldown': 'consumption'
                })

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        insurance = []
        for tag in budget.insurance_tags.annotate(name_lower=Func(F('name'), function='LOWER')).order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('pk', 'account__unit', 'amount'):
                if e['pk'] not in entry_ids:
                    amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
                    entry_ids.add(e['pk'])
            unit = None
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                insurance.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'insurance' not in drilldown[0][unit]:
                    drilldown[0][unit]['insurance'] = fbudget.make_drilldown(str(_('Insurance')), 'insurance', unit)
                    drilldown[1][unit]['insurance'] = fbudget.make_drilldown(str(_('Insurance')), 'insurance', unit)
                drilldown[0][unit]['insurance']['data'].append({
                    'name': tag.name,
                    'y': abs(v) / 12,
                    'drilldown': 'insurance_%s' % tag.slug
                })
                drilldown[1][unit]['insurance']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': 'insurance_%s' % tag.slug
                })
            if unit:
                drilldown[0][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'insurance_%s' % tag.slug, unit)
                drilldown[1][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'insurance_%s' % tag.slug, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                    if entry.category.slug in categories[0]:
                        categories[0][entry.category.slug]['y'] += entry.amount
                        categories[1][entry.category.slug]['y'] += entry.amount
                    else:
                        categories[0][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                        categories[1][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['y']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['y'])
                drilldown[0][unit][tag.slug]['data'] = [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.slug]['data'] = [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                footer[7][k] = footer[7][k] + (v / 12) if k in footer[7] else (v / 12)
                footer[8][k] = footer[8][k] + v if k in footer[8] else v
        units.update(footer[7].keys())
        for unit in units:
            if unit not in series[0] and unit in footer[8]:
                series[0][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name})), unit)
                series[1][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name})), unit)
            if unit in footer[8]:
                series[0][unit]['data'].append({
                    'name': str(_('Insurance')),
                    'y': abs(footer[8][unit]) / 12,
                    'drilldown': 'insurance'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Insurance')),
                    'y': abs(footer[8][unit]),
                    'drilldown': 'insurance'
                })

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        savings = []
        for tag in budget.savings_tags.annotate(name_lower=Func(F('name'), function='LOWER')).order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(tags__pk=tag.pk)).values('pk', 'account__unit', 'amount'):
                if e['pk'] not in entry_ids:
                    amounts[e['account__unit']] = amounts[e['account__unit']] + e['amount'] if e['account__unit'] in amounts else e['amount']
                    entry_ids.add(e['pk'])
            unit = None
            for i, (k, v) in enumerate(amounts.items()):
                unit = Unit.objects.get(pk=k)
                amounts[unit] = amounts.pop(k)
                savings.append({
                    'slug': tag.slug if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'savings' not in drilldown[0][unit]:
                    drilldown[0][unit]['savings'] = fbudget.make_drilldown(str(_('Savings')), 'savings', unit)
                    drilldown[1][unit]['savings'] = fbudget.make_drilldown(str(_('Savings')), 'savings', unit)
                drilldown[0][unit]['savings']['data'].append({
                    'name': tag.name,
                    'y': abs(v) / 12,
                    'drilldown': 'savings_%s' % tag.slug
                })
                drilldown[1][unit]['savings']['data'].append({
                    'name': tag.name,
                    'y': abs(v),
                    'drilldown': 'savings_%s' % tag.slug
                })
            if unit:
                drilldown[0][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'savings_%s' % tag.slug, unit)
                drilldown[1][unit][tag.slug] = fbudget.make_drilldown(tag.name, 'savings_%s' % tag.slug, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(account__in=ledger.accounts.all()).filter(day__year=year).filter(account__unit=unit).filter(tags=tag):
                    if entry.category.slug in categories[0]:
                        categories[0][entry.category.slug]['y'] += entry.amount
                        categories[1][entry.category.slug]['y'] += entry.amount
                    else:
                        categories[0][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                        categories[1][entry.category.slug] = {
                            'name': entry.category.name,
                            'y': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['y']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['y'])
                drilldown[0][unit][tag.slug]['data'] = [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.slug]['data'] = [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                footer[10][k] = footer[10][k] + (v / 12) if k in footer[10] else (v / 12)
                footer[11][k] = footer[11][k] + v if k in footer[11] else v
        units.update(footer[10].keys())
        for unit in units:
            if unit not in series[0] and unit in footer[11]:
                series[0][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name})), unit)
                series[1][unit] = fbudget.make_series(str(_('Budget %(unit)s' % {'unit': unit.name})), unit)
            if unit in footer[11]:
                series[0][unit]['data'].append({
                    'name': str(_('Savings')),
                    'y': abs(footer[11][unit]) / 12,
                    'drilldown': 'savings'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Savings')),
                    'y': abs(footer[11][unit]),
                    'drilldown': 'savings'
                })

        for unit in units:
            msum = Entry.objects.exclude(pk__in=entry_ids).exclude(category__accounts__in=ledger.accounts.all()).filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(account__unit=unit)).aggregate(Sum('amount'))['amount__sum']
            if unit in series[0] and msum:
                series[0][unit]['data'].append({
                    'name': str(_('Rest')),
                    'y': abs(msum) / 12,
                    'drilldown': 'rest'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Rest')),
                    'y': abs(msum),
                    'drilldown': 'rest'
                })

            drilldown[0][unit]['rest'] = fbudget.make_drilldown(str(_('Rest')), 'rest', unit)
            drilldown[1][unit]['rest'] = fbudget.make_drilldown(str(_('Rest')), 'rest', unit)
            drilldown[0][unit]['rest2'] = fbudget.make_drilldown(str(_('Rest')), 'rest2', unit)
            drilldown[1][unit]['rest2'] = fbudget.make_drilldown(str(_('Rest')), 'rest2', unit)
            rest = {'rest2': {'name': _('Rest'), 'amount': 0, 'categories': {}}}
            for e in Entry.objects.exclude(pk__in=entry_ids).exclude(category__accounts__in=ledger.accounts.all()).filter(Q(account__in=ledger.accounts.all()) & Q(day__year=year) & Q(account__unit=unit)):
                if e.pk not in entry_ids:
                    t = e.tags.first()
                    if t:
                        if t.slug not in rest:
                            rest[t.slug] = {'name': t.name, 'amount': 0, 'categories': {}}
                        rest[t.slug]['amount'] += e.amount
                        if e.category.slug not in rest[t.slug]['categories']:
                            rest[t.slug]['categories'][e.category.slug] = {'name': e.category.name, 'amount': 0}
                            drilldown[0][unit]['rest_%s' % t.slug] = fbudget.make_drilldown(e.category.name, 'rest_%s' % t.slug, unit)
                            drilldown[1][unit]['rest_%s' % t.slug] = fbudget.make_drilldown(e.category.name, 'rest_%s' % t.slug, unit)
                        rest[t.slug]['categories'][e.category.slug]['amount'] += e.amount
                    else:
                        rest['rest2']['amount'] += e.amount
                        if e.category.slug not in rest['rest2']['categories']:
                            rest['rest2']['categories'][e.category.slug] = {'name': e.category.name, 'amount': 0}
                            drilldown[0][unit]['rest_rest2'] = fbudget.make_drilldown(e.category.name, 'rest_rest2', unit)
                            drilldown[1][unit]['rest_rest2'] = fbudget.make_drilldown(e.category.name, 'rest_rest2', unit)
                        rest['rest2']['categories'][e.category.slug]['amount'] += e.amount
                    entry_ids.add(e.pk)

            for k, v in rest.items():
                if v:
                    drilldown[0][unit]['rest']['data'].append({
                        'name': str(v['name']),
                        'y': abs(v['amount']) / 12,
                        'drilldown': 'rest_%s' % k
                    })
                    drilldown[1][unit]['rest']['data'].append({
                        'name': str(v['name']),
                        'y': abs(v['amount']),
                        'drilldown': 'rest_%s' % k
                    })
                    for category, v2 in v['categories'].items():
                        drilldown[0][unit]['rest_%s' % k]['data'].append({
                            'name': str(v2['name']),
                            'y': abs(v2['amount']) / 12
                        })
                        drilldown[1][unit]['rest_%s' % k]['data'].append({
                            'name': str(v2['name']),
                            'y': abs(v2['amount'])
                        })

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
        if len(series[0]) == 1:
            series_monthly = json.dumps([v for k, v in series[0].items()])
            series_yearly = json.dumps([v for k, v in series[1].items()])
            drilldown_monthly = json.dumps({'series': [s for k, v in drilldown[0].items() for k2, s in drilldown[0][k].items()]})
            drilldown_yearly = json.dumps({'series': [s for k, v in drilldown[1].items() for k2, s in drilldown[1][k].items()]})
        else:
            series_monthly = dict((k.id, json.dumps([v])) for k, v in series[0].items())
            series_yearly = dict((k.id, json.dumps([v])) for k, v in series[1].items())
            drilldown_monthly = dict((k.id, json.dumps({'series': [v2 for k2, v2 in v.items()]})) for k, v in drilldown[0].items())
            drilldown_yearly = dict((k.id, json.dumps({'series': [v2 for k2, v2 in v.items()]})) for k, v in drilldown[1].items())
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
