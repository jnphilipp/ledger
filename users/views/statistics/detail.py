# -*- coding: utf-8 -*-

from accounts.models import Entry
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from units.models import Unit
from users.models import Ledger


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Ledger
    template_name = 'users/statistics_detail.html'

    def get_object(self, queryset=None):
        return Ledger.objects.get(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)

        if 'unit' in self.kwargs:
            context['unit'] = get_object_or_404(Unit, slug=self.kwargs['unit'])
            accounts = self.object.accounts.filter(unit=context['unit'])
        else:
            units = Unit.objects.filter(accounts__ledger=self.object). \
                distinct()

            context['option_msg'] = _('Select a unit')
            context['options'] = [{
                'id': unit.slug,
                'key': 'unit',
                'value': unit.name
            } for unit in units]

            return context

        if 'chart' in self.kwargs:
            context['chart'] = self.kwargs['chart']

            if context['chart'] == 'tags':
                context['chart_name'] = _('Tags')
            elif context['chart'] == 'categories':
                context['chart_name'] = _('Categories')
            else:
                return context
        else:
            context['option_msg'] = _('Select a chart')
            context['options'] = [{
                'id': 'categories',
                'key': 'chart',
                'value': _('Categories')
            }, {
                'id': 'tags',
                'key': 'chart',
                'value': _('Tags')
            }]

            return context

        if 'year' in self.kwargs:
            context['year'] = self.kwargs['year']
        else:
            years = Entry.objects.filter(account__in=accounts).dates('day',
                                                                     'year')
            if context['chart'] == 'tags':
                years = years.filter(tags__isnull=False)

            context['option_msg'] = _('Select a year')
            context['options'] = [{
                'id': year.strftime('%Y'),
                'key': 'year',
                'value': year.strftime('%Y')
            } for year in years]

            return context

        if 'month' in self.kwargs:
            context['month'] = self.kwargs['month']
            context['month_name'] = date(year=context['year'],
                                         month=context['month'],
                                         day=1).strftime('%B')
        else:
            months = Entry.objects.filter(account__in=accounts). \
                filter(day__year=context['year']).dates('day', 'month')
            if context['chart'] == 'tags':
                months = months.filter(tags__isnull=False)

            context['option_msg'] = _('Select a month')
            context['options'] = [{
                'id': month.strftime('%m'),
                'key': 'month',
                'value': _(month.strftime('%B'))
            } for month in months]

        return context
