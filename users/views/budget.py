# -*- coding: utf-8 -*-

import json

from accounts.models import Entry
from accounts.templatetags.accounts import colorfy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Func, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from units.models import Unit
from users.forms import BudgetForm
from users.models import Budget, Ledger


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Budget

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)

        years = Entry.objects.filter(
            account__ledger__user=self.request.user).dates('day', 'year')
        context['years'] = [y.year for y in years]

        if 'year' in self.kwargs:
            year = self.kwargs['year']
        else:
            y = timezone.now().year
            if y in context['years']:
                year = y
            else:
                year = context['years'][-1]

        entry_ids = set()
        units = set()
        series = [{}, {}]
        drilldown = [{}, {}]

        footer = []
        footer.append(_('Sum'))
        footer.append({})
        footer.append({})

        income = []
        for tag in self.object.income_tags.annotate(name_lower=Func(F('name'),
                                                    function='LOWER')). \
                order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(
                    Q(account__ledger__user=self.request.user) &
                    Q(day__year=year) & Q(tags__pk=tag.pk)):
                if e.pk not in entry_ids:
                    entry_ids.add(e.pk)
                    if e.account.unit in amounts:
                        amounts[e.account.unit] += e.amount
                    else:
                        amounts[e.account.unit] = e.amount

            unit = None
            for i, (unit, v) in enumerate(amounts.items()):
                income.append({
                    'pk': tag.pk if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'income' not in drilldown[0][unit]:
                    drilldown[0][unit]['income'] = \
                        self.drilldown(_('Income'), 'income', unit)
                    drilldown[1][unit]['income'] = \
                        self.drilldown(_('Income'), 'income', unit)
                drilldown[0][unit]['income']['data'].append({
                    'name': tag.name,
                    'v': v / 12,
                    'y': abs(v) / 12,
                    'drilldown': 'income_%s' % tag.pk
                })
                drilldown[1][unit]['income']['data'].append({
                    'name': tag.name,
                    'v': v,
                    'y': abs(v),
                    'drilldown': 'income_%s' % tag.pk
                })
            if unit:
                drilldown[0][unit][tag.pk] = \
                    self.drilldown(tag.name, 'income_%s' % tag.pk, unit)
                drilldown[1][unit][tag.pk] = \
                    self.drilldown(tag.name, 'income_%s' % tag.pk, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(
                        Q(account__ledger__user=self.request.user) &
                        Q(day__year=year) & Q(account__unit=unit) &
                        Q(tags=tag)):
                    if entry.category.pk in categories[0]:
                        categories[0][entry.category.pk]['v'] += entry.amount
                        categories[1][entry.category.pk]['v'] += entry.amount
                    else:
                        categories[0][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                        categories[1][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['v']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['v'])
                drilldown[0][unit][tag.pk]['data'] = \
                    [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.pk]['data'] = \
                    [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                if k in footer[1]:
                    footer[1][k] += (v / 12)
                else:
                    footer[1][k] = (v / 12)
                if k in footer[2]:
                    footer[2][k] += v
                else:
                    footer[2][k] = v
        units.update(footer[1].keys())
        for unit in units:
            if len(units) > 1:
                name = _('Budget %(unit)s' % {'unit': unit.name})
            else:
                name = _('Budget')
            series[0][unit] = self.series(name, unit)
            series[1][unit] = self.series(name, unit)
            series[0][unit]['data'].append({
                'name': str(_('Income')),
                'v': footer[2][unit] / 12,
                'y': abs(footer[2][unit]) / 12,
                'drilldown': 'income'
            })
            series[1][unit]['data'].append({
                'name': str(_('Income')),
                'v': footer[2][unit],
                'y': abs(footer[2][unit]),
                'drilldown': 'income'
            })

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        consumption = []
        for tag in self.object.consumption_tags.annotate(
                name_lower=Func(F('name'), function='LOWER')). \
                order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(
                    Q(account__ledger__user=self.request.user) &
                    Q(day__year=year) & Q(tags__pk=tag.pk)):
                if e.pk not in entry_ids:
                    entry_ids.add(e.pk)
                    if e.account.unit in amounts:
                        amounts[e.account.unit] += e.amount
                    else:
                        amounts[e.account.unit] = e.amount

            unit = None
            for i, (unit, v) in enumerate(amounts.items()):
                consumption.append({
                    'pk': tag.pk if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'consumption' not in drilldown[0][unit]:
                    drilldown[0][unit]['consumption'] = \
                        self.drilldown(_('Consumption'), 'consumption', unit)
                    drilldown[1][unit]['consumption'] = \
                        self.drilldown(_('Consumption'), 'consumption', unit)
                drilldown[0][unit]['consumption']['data'].append({
                    'name': tag.name,
                    'v': v / 12,
                    'y': abs(v) / 12,
                    'drilldown': 'consumption_%s' % tag.pk
                })
                drilldown[1][unit]['consumption']['data'].append({
                    'name': tag.name,
                    'v': v,
                    'y': abs(v),
                    'drilldown': 'consumption_%s' % tag.pk
                })
            if unit:
                drilldown[0][unit][tag.pk] = \
                    self.drilldown(tag.name, 'consumption_%s' % tag.pk, unit)
                drilldown[1][unit][tag.pk] = \
                    self.drilldown(tag.name, 'consumption_%s' % tag.pk, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(
                        Q(account__ledger__user=self.request.user) &
                        Q(day__year=year) & Q(account__unit=unit) &
                        Q(tags=tag)):
                    if entry.category.pk in categories[0]:
                        categories[0][entry.category.pk]['v'] += entry.amount
                        categories[1][entry.category.pk]['v'] += entry.amount
                    else:
                        categories[0][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                        categories[1][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['v']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['v'])
                drilldown[0][unit][tag.pk]['data'] = \
                    [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.pk]['data'] = \
                    [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                if k in footer[4]:
                    footer[4][k] += (v / 12)
                else:
                    footer[4][k] = (v / 12)
                footer[5][k] = footer[5][k] + v if k in footer[5] else v
        units.update(footer[4].keys())
        for unit in units:
            if unit not in series[0] and unit in footer[5]:
                name = _('Budget %(unit)s') % {'unit': unit.name}
                series[0][unit] = self.series(name, unit)
                series[1][unit] = self.series(name, unit)
            if unit in footer[5]:
                series[0][unit]['data'].append({
                    'name': str(_('Consumption')),
                    'v': footer[5][unit] / 12,
                    'y': abs(footer[5][unit]) / 12,
                    'drilldown': 'consumption'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Consumption')),
                    'v': footer[5][unit],
                    'y': abs(footer[5][unit]),
                    'drilldown': 'consumption'
                })

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        insurance = []
        for tag in self.object.insurance_tags.annotate(
                name_lower=Func(F('name'), function='LOWER')). \
                order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(
                    Q(account__ledger__user=self.request.user) &
                    Q(day__year=year) & Q(tags__pk=tag.pk)):
                if e.pk not in entry_ids:
                    entry_ids.add(e.pk)
                    if e.account.unit in amounts:
                        amounts[e.account.unit] += e.amount
                    else:
                        amounts[e.account.unit] = e.amount

            unit = None
            for i, (unit, v) in enumerate(amounts.items()):
                insurance.append({
                    'pk': tag.pk if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'insurance' not in drilldown[0][unit]:
                    drilldown[0][unit]['insurance'] = \
                        self.drilldown(_('Insurance'), 'insurance', unit)
                    drilldown[1][unit]['insurance'] = \
                        self.drilldown(_('Insurance'), 'insurance', unit)
                drilldown[0][unit]['insurance']['data'].append({
                    'name': tag.name,
                    'v': v / 12,
                    'y': abs(v) / 12,
                    'drilldown': 'insurance_%s' % tag.pk
                })
                drilldown[1][unit]['insurance']['data'].append({
                    'name': tag.name,
                    'v': v,
                    'y': abs(v),
                    'drilldown': 'insurance_%s' % tag.pk
                })
            if unit:
                drilldown[0][unit][tag.pk] = \
                    self.drilldown(tag.name, 'insurance_%s' % tag.pk, unit)
                drilldown[1][unit][tag.pk] = \
                    self.drilldown(tag.name, 'insurance_%s' % tag.pk, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(
                        Q(account__ledger__user=self.request.user) &
                        Q(day__year=year) & Q(account__unit=unit) &
                        Q(tags=tag)):
                    if entry.category.pk in categories[0]:
                        categories[0][entry.category.pk]['v'] += entry.amount
                        categories[1][entry.category.pk]['v'] += entry.amount
                    else:
                        categories[0][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                        categories[1][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['v']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['v'])
                drilldown[0][unit][tag.pk]['data'] = \
                    [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.pk]['data'] = \
                    [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                if k in footer[7]:
                    footer[7][k] += (v / 12)
                else:
                    footer[7][k] = (v / 12)
                footer[8][k] = footer[8][k] + v if k in footer[8] else v
        units.update(footer[7].keys())
        for unit in units:
            if unit not in series[0] and unit in footer[8]:
                name = _('Budget %(unit)s') % {'unit': unit.name}
                series[0][unit] = self.series(name, unit)
                series[1][unit] = self.series(name, unit)
            if unit in footer[8]:
                series[0][unit]['data'].append({
                    'name': str(_('Insurance')),
                    'v': footer[8][unit] / 12,
                    'y': abs(footer[8][unit]) / 12,
                    'drilldown': 'insurance'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Insurance')),
                    'v': footer[8][unit],
                    'y': abs(footer[8][unit]),
                    'drilldown': 'insurance'
                })

        footer.append(_('Sum'))
        footer.append({})
        footer.append({})
        savings = []
        for tag in self.object.savings_tags.annotate(name_lower=Func(F('name'),
                                                     function='LOWER')). \
                order_by('name_lower'):
            amounts = {}
            for e in Entry.objects.filter(
                    Q(account__ledger__user=self.request.user) &
                    Q(day__year=year) & Q(tags__pk=tag.pk)):
                if e.pk not in entry_ids:
                    entry_ids.add(e.pk)
                    if e.account.unit in amounts:
                        amounts[e.account.unit] += e.amount
                    else:
                        amounts[e.account.unit] = e.amount

            unit = None
            for i, (unit, v) in enumerate(amounts.items()):
                savings.append({
                    'pk': tag.pk if i < 1 else '',
                    'name': tag.name if i < 1 else '',
                    'monthly': colorfy(v / 12, unit),
                    'yearly': colorfy(v, unit)
                })
                if unit not in drilldown[0]:
                    drilldown[0][unit] = {}
                    drilldown[1][unit] = {}
                if 'savings' not in drilldown[0][unit]:
                    drilldown[0][unit]['savings'] = \
                        self.drilldown(_('Savings'), 'savings', unit)
                    drilldown[1][unit]['savings'] = \
                        self.drilldown(_('Savings'), 'savings', unit)
                drilldown[0][unit]['savings']['data'].append({
                    'name': tag.name,
                    'v': v / 12,
                    'y': abs(v) / 12,
                    'drilldown': 'savings_%s' % tag.pk
                })
                drilldown[1][unit]['savings']['data'].append({
                    'name': tag.name,
                    'v': v,
                    'y': abs(v),
                    'drilldown': 'savings_%s' % tag.pk
                })
            if unit:
                drilldown[0][unit][tag.pk] = \
                    self.drilldown(tag.name, 'savings_%s' % tag.pk, unit)
                drilldown[1][unit][tag.pk] = \
                    self.drilldown(tag.name, 'savings_%s' % tag.pk, unit)
                categories = [{}, {}]
                for entry in Entry.objects.filter(
                        Q(account__ledger__user=self.request.user) &
                        Q(day__year=year) & Q(account__unit=unit) &
                        Q(tags=tag)):
                    if entry.category.pk in categories[0]:
                        categories[0][entry.category.pk]['v'] += entry.amount
                        categories[1][entry.category.pk]['v'] += entry.amount
                    else:
                        categories[0][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                        categories[1][entry.category.pk] = {
                            'name': entry.category.name,
                            'v': entry.amount
                        }
                for k in categories[0].keys():
                    categories[0][k]['y'] = abs(categories[0][k]['v']) / 12
                    categories[1][k]['y'] = abs(categories[1][k]['v'])
                drilldown[0][unit][tag.pk]['data'] = \
                    [v for k, v in categories[0].items()]
                drilldown[1][unit][tag.pk]['data'] = \
                    [v for k, v in categories[1].items()]
            for k, v in amounts.items():
                if k in footer[10]:
                    footer[10][k] += (v / 12)
                else:
                    footer[10][k] = (v / 12)
                footer[11][k] = footer[11][k] + v if k in footer[11] else v
        units.update(footer[10].keys())
        for unit in units:
            if unit not in series[0] and unit in footer[11]:
                name = _('Budget %(unit)s' % {'unit': unit.name})
                series[0][unit] = self.series(name, unit)
                series[1][unit] = self.series(name, unit)
            if unit in footer[11]:
                series[0][unit]['data'].append({
                    'name': str(_('Savings')),
                    'v': footer[11][unit] / 12,
                    'y': abs(footer[11][unit]) / 12,
                    'drilldown': 'savings'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Savings')),
                    'v': footer[11][unit],
                    'y': abs(footer[11][unit]),
                    'drilldown': 'savings'
                })

        for unit in units:
            msum = Entry.objects.exclude(pk__in=entry_ids). \
                exclude(category__accounts__ledger__user=self.request.user). \
                filter(Q(account__ledger__user=self.request.user) &
                       Q(day__year=year) & Q(account__unit=unit)). \
                aggregate(Sum('amount'))['amount__sum']
            if unit in series[0] and msum:
                series[0][unit]['data'].append({
                    'name': str(_('Rest')),
                    'v': msum / 12,
                    'y': abs(msum) / 12,
                    'drilldown': 'r'
                })
                series[1][unit]['data'].append({
                    'name': str(_('Rest')),
                    'v': msum,
                    'y': abs(msum),
                    'drilldown': 'r'
                })

            drilldown[0][unit]['r'] = self.drilldown(_('Rest'), 'r', unit)
            drilldown[1][unit]['r'] = self.drilldown(_('Rest'), 'r', unit)
            drilldown[0][unit]['r2'] = self.drilldown(_('Rest'), 'r2', unit)
            drilldown[1][unit]['r2'] = self.drilldown(_('Rest'), 'r2', unit)
            rest = {
                'r2': {
                    'name': _('Rest'),
                    'amount': 0,
                    'categories': {}
                }
            }
            entries = Entry.objects.exclude(pk__in=entry_ids). \
                exclude(category__accounts__ledger__user=self.request.user). \
                filter(Q(account__ledger__user=self.request.user) &
                       Q(day__year=year) & Q(account__unit=unit))
            for e in entries:
                if e.pk not in entry_ids:
                    t = e.tags.first()
                    if t:
                        if t.pk not in rest:
                            rest[t.pk] = {'name': t.name, 'amount': 0,
                                          'categories': {}}
                        rest[t.pk]['amount'] += e.amount

                        if e.category.pk not in rest[t.pk]['categories']:
                            rest[t.pk]['categories'][e.category.pk] = \
                                {'name': e.category.name, 'amount': 0}

                            id = 'r_%s' % t.pk
                            drilldown[0][unit][id] = \
                                self.drilldown(e.category.name, id, unit)
                            drilldown[1][unit][id] = \
                                self.drilldown(e.category.name, id, unit)
                        rest[t.pk]['categories'][e.category.pk]['amount'] += \
                            e.amount
                    else:
                        rest['r2']['amount'] += e.amount
                        if e.category.pk not in rest['r2']['categories']:
                            rest['r2']['categories'][e.category.pk] = \
                                {'name': e.category.name, 'amount': 0}
                            drilldown[0][unit]['r_r2'] = \
                                self.drilldown(e.category.name, 'r_r2', unit)
                            drilldown[1][unit]['r_r2'] = \
                                self.drilldown(e.category.name, 'r_r2', unit)
                        rest['r2']['categories'][e.category.pk]['amount'] += \
                            e.amount
                    entry_ids.add(e.pk)

            for k, v in rest.items():
                if v:
                    drilldown[0][unit]['r']['data'].append({
                        'name': str(v['name']),
                        'v': v['amount'] / 12,
                        'y': abs(v['amount']) / 12,
                        'drilldown': 'r_%s' % k
                    })
                    drilldown[1][unit]['r']['data'].append({
                        'name': str(v['name']),
                        'v': v['amount'],
                        'y': abs(v['amount']),
                        'drilldown': 'r_%s' % k
                    })
                    for category, v2 in v['categories'].items():
                        if v2['amount']:
                            drilldown[0][unit]['r_%s' % k]['data'].append({
                                'name': str(v2['name']),
                                'v': v2['amount'] / 12,
                                'y': abs(v2['amount']) / 12
                            })
                            drilldown[1][unit]['r_%s' % k]['data'].append({
                                'name': str(v2['name']),
                                'v': v2['amount'],
                                'y': abs(v2['amount'])
                            })

        footer = [footer.copy() for unit in units]
        for i, unit in enumerate(units):
            if i > 0:
                footer[i][0] = footer[i][3] = footer[i][6] = footer[i][9] = ''

            footer.append(['', '', '', '', '', '', '', '', '',
                           _('Total') if i == 0 else '', 0, 0])
            footer[-1][10] = \
                (footer[i][1][unit] if unit in footer[i][1] else 0) + \
                (footer[i][4][unit] if unit in footer[i][4] else 0) + \
                (footer[i][7][unit] if unit in footer[i][7] else 0) + \
                (footer[i][10][unit] if unit in footer[i][10] else 0)
            footer[-1][11] = \
                (footer[i][2][unit] if unit in footer[i][2] else 0) + \
                (footer[i][5][unit] if unit in footer[i][5] else 0) + \
                (footer[i][8][unit] if unit in footer[i][8] else 0) + \
                (footer[i][11][unit] if unit in footer[i][11] else 0)

            footer[i][1] = colorfy(footer[i][1][unit], unit) \
                if unit in footer[i][1] else ''
            footer[i][2] = colorfy(footer[i][2][unit], unit) \
                if unit in footer[i][2] else ''
            footer[i][4] = colorfy(footer[i][4][unit], unit) \
                if unit in footer[i][4] else ''
            footer[i][5] = colorfy(footer[i][5][unit], unit) \
                if unit in footer[i][5] else ''
            footer[i][7] = colorfy(footer[i][7][unit], unit) \
                if unit in footer[i][7] else ''
            footer[i][8] = colorfy(footer[i][8][unit], unit) \
                if unit in footer[i][8] else ''
            footer[i][10] = colorfy(footer[i][10][unit], unit) \
                if unit in footer[i][10] else ''
            footer[i][11] = colorfy(footer[i][11][unit], unit) \
                if unit in footer[i][11] else ''
            footer[-1][10] = colorfy(footer[-1][10], unit)
            footer[-1][11] = colorfy(footer[-1][11], unit)

        for i, unit in enumerate(units):
            real = Entry.objects. \
                exclude(category__accounts__ledger__user=self.request.user).\
                filter(Q(account__ledger__user=self.request.user) &
                       Q(account__unit=unit) & Q(day__year=year)). \
                aggregate(sum=Sum('amount'))['sum']
            footer.append(['', '', '', '', '', '', '', '', '',
                           _('Real') if i == 0 else '', 0, 0])
            footer[-1][10] = colorfy(real / 12, unit)
            footer[-1][11] = colorfy(real, unit)

        table = []
        for i in range(max(len(income), len(consumption), len(insurance),
                           len(savings))):
            row = []
            if i < len(income):
                row.append([income[i]['pk'],
                            income[i]['name']] if income[i]['name'] else '')
                row.append(income[i]['monthly'])
                row.append(income[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(consumption):
                row.append([consumption[i]['pk'], consumption[i]['name']]
                           if consumption[i]['name'] else '')
                row.append(consumption[i]['monthly'])
                row.append(consumption[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(insurance):
                row.append([insurance[i]['pk'], insurance[i]['name']]
                           if insurance[i]['name'] else '')
                row.append(insurance[i]['monthly'])
                row.append(insurance[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(savings):
                row.append([savings[i]['pk'],
                            savings[i]['name']] if savings[i]['name'] else '')
                row.append(savings[i]['monthly'])
                row.append(savings[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            table.append(row)

        context['footer'] = footer
        context['table'] = table
        context['units'] = units
        context['year'] = year
        if len(series[0]) == 1:
            monthly = json.dumps([v for k, v in series[0].items()])
            yearly = json.dumps([v for k, v in series[1].items()])
            dmonthly = json.dumps({
                'series': [s for k, v in drilldown[0].items()
                           for k2, s in drilldown[0][k].items()]
            })
            dyearly = json.dumps({
                'series': [s for k, v in drilldown[1].items()
                           for k2, s in drilldown[1][k].items()]
            })
        else:
            monthly = dict((k.id, json.dumps([v]))
                           for k, v in series[0].items())
            yearly = dict((k.id, json.dumps([v]))
                          for k, v in series[1].items())
            dmonthly = dict((k.id, json.dumps({
                'series': [v2 for k2, v2 in v.items()]
            })) for k, v in drilldown[0].items())
            dyearly = dict((k.id, json.dumps({
                'series': [v2 for k2, v2 in v.items()]
            })) for k, v in drilldown[1].items())

        context['series_monthly'] = monthly
        context['series_yearly'] = yearly
        context['drilldown_monthly'] = dmonthly
        context['drilldown_yearly'] = dyearly
        return context

    def get_object(self, queryset=None):
        return Budget.objects.get(user=self.request.user)

    def series(self, name, unit):
        return {
            'name': '%s' % name,
            'colorByPoint': True,
            'dataLabels': {
                'enabled': True,
                'format': '{point.name}: {point.v:.%df} %s' % (unit.precision,
                                                               unit.symbol)
            },
            'tooltip': {
                'headerFormat': '<span style="font-size:11px">' +
                                '{series.name}</span><br>',
                'pointFormat': ('<span style="color:{point.color}">' +
                                '{point.name}</span>: <b>{point.v:.%df} %s' +
                                '</b><br/>') % (unit.precision, unit.symbol)
            },
            'data': []
        }

    def drilldown(self, name, id, unit):
        return {
            'name': '%s' % name,
            'id': id,
            'dataLabels': {
                'enabled': True,
                'format': '{point.name}: {point.v:.%df} %s' % (unit.precision,
                                                               unit.symbol)
            },
            'tooltip': {
                'headerFormat': '<span style="font-size:11px">' +
                                '{series.name}</span><br>',
                'pointFormat': ('<span style="color:{point.color}">' +
                                '{point.name}</span>: <b>{point.v:.%df} %s' +
                                '</b><br/>') % (unit.precision, unit.symbol)
            },
            'data': []
        }


@method_decorator(login_required, name='dispatch')
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = BudgetForm
    model = Budget
    success_message = _('Your budget was successfully updated.')

    def get_object(self, queryset=None):
        return Budget.objects.get(user=self.request.user)
