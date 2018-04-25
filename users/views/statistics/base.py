# -*- coding: utf-8 -*-

from accounts.models import Entry
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext_lazy as _
from units.models import Unit
from users.models import Ledger


@login_required
def detail(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    unit_slug = request.GET.get('unit')
    chart = request.GET.get('chart')
    year = request.GET.get('year')
    month = request.GET.get('month')

    if year and month:
        month_name = date(year=int(year), month=int(month),
                          day=1).strftime('%B')

    options = []
    if not unit_slug:
        option_msg = _('Select a unit')
        options = [{
            'id': unit.slug,
            'key': 'unit',
            'value': unit.name
        } for unit in Unit.objects.filter(accounts__ledger=ledger).distinct()]
    else:
        unit = get_object_or_404(Unit, slug=unit_slug)
        accounts = ledger.accounts.filter(unit=unit)
        if unit_slug and not chart:
            option_msg = _('Select a chart')
            options = [{
                'id': 'categories',
                'key': 'chart',
                'value': _('Categories')
            }, {
                'id': 'tags',
                'key': 'chart',
                'value': _('Tags')
            }]
        elif unit_slug and chart and not year:
            years = Entry.objects.filter(account__in=accounts).dates('day',
                                                                     'year')
            if chart == 'tags':
                chart_name = _('Tags')
                years = years.filter(tags__isnull=False)
            else:
                chart_name = _('Categories')

            option_msg = _('Select a year')
            options = [{
                'id': year.strftime('%Y'),
                'key': 'year',
                'value': year.strftime('%Y')} for year in years]
        elif unit_slug and chart and year and not month:
            months = Entry.objects.filter(account__in=accounts). \
                filter(day__year=year).dates('day', 'month')
            if chart == 'tags':
                chart_name = _('Tags')
                months = months.filter(tags__isnull=False)
            else:
                chart_name = _('Categories')

            option_msg = _('Select a month')
            options = [{
                'id': month.strftime('%m'),
                'key': 'month',
                'value': _(month.strftime('%B'))
            } for month in months]
        elif unit_slug and chart and year and month:
            option_msg = None
            chart_name = _('Tags') if chart == 'tags' else _('Categories')
    return render(request, 'users/statistics.html', locals())
