# -*- coding: utf-8 -*-

from accounts.models import Entry
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from units.models import Unit
from users.models import Ledger


@login_required
def statistics(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    unit_slug = request.GET.get('unit')
    chart = request.GET.get('chart')
    year = request.GET.get('year')
    month = request.GET.get('month')

    if year and month:
        month_name = date(year=int(year), month=int(month), day=1).strftime('%B').lower()

    options = []
    if not unit_slug:
        option_name = 'unit'
        options = [{'id':unit.slug, 'key':'unit', 'value':unit.name.lower()} for unit in Unit.objects.filter(accounts__ledger=ledger).distinct()]
    else:
        unit = get_object_or_404(Unit, slug=unit_slug)
        if unit_slug and not chart:
            option_name = 'chart'
            options = [{'id':'categories', 'key':'chart', 'value':'categories'}, {'id':'tags', 'key':'chart', 'value':'tags'}]
        elif unit_slug and chart and not year:
            years = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).dates('day', 'year')
            if chart == 'tags':
                years = years.filter(tags__isnull=False)

            option_name = 'year'
            options = [{'id':year.strftime('%Y'), 'key':'year', 'value':year.strftime('%Y')} for year in years]
        elif unit_slug and chart and year and not month:
            months = Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).filter(day__year=year).dates('day', 'month')
            if chart == 'tags':
                months = months.filter(tags__isnull=False)

            option_name = 'month'
            options = [{'id':month.strftime('%m'), 'key':'month', 'value':month.strftime('%B').lower()} for month in months]
        elif unit_slug and chart and year and month:
            option_name = None
    return render(request, 'users/statistics.html', locals())
