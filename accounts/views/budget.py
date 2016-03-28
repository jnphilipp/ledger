# -*- coding: utf-8 -*-

from accounts.models import Entry, Unit
from accounts.templatetags.accounts import colorfy
from app.forms import BudgetForm
from app.models import Budget, Ledger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

@login_required(login_url='/profile/signin/')
def budget(request):
    ledger = get_object_or_404(Ledger, user=request.user)
    budget = get_object_or_404(Budget, user=request.user)
    units = Unit.objects.filter(account__ledger=ledger).distinct()

    unit_slug = request.GET.get('unit')
    year = request.GET.get('year')
    if unit_slug:
        unit = get_object_or_404(Unit, slug='euro')
        years = [y.strftime('%Y') for y in Entry.objects.filter(account__in=ledger.accounts.filter(unit=unit)).dates('day', 'year')]
        year = years[-1]
    if year:
        footer = []
        footer.append('sum')
        footer.append(0)
        footer.append(0)

        income = []
        for tag in budget.income_tags.all():
            e = Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(tags__pk=tag.pk)).aggregate(sum=Sum('amount'))
            if e['sum']:
                income.append({'name':tag.name.lower(), 'monthly':colorfy(e['sum']/12, unit), 'yearly':colorfy(e['sum'], unit)})
                footer[1] += e['sum']/12
                footer[2] += e['sum']

        footer.append('sum')
        footer.append(0)
        footer.append(0)
        consumption = []
        for tag in budget.consumption_tags.all():
            e = Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(tags__pk=tag.pk)).aggregate(sum=Sum('amount'))
            if e['sum']:
                consumption.append({'name':tag.name.lower(), 'monthly':colorfy(e['sum']/12, unit), 'yearly':colorfy(e['sum'], unit)})
                footer[4] += e['sum']/12
                footer[5] += e['sum']


        footer.append('sum')
        footer.append(0)
        footer.append(0)
        insurance = []
        for tag in budget.insurance_tags.all():
            e = Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(tags__pk=tag.pk)).aggregate(sum=Sum('amount'))
            if e['sum']:
                insurance.append({'name':tag.name.lower(), 'monthly':colorfy(e['sum']/12, unit), 'yearly':colorfy(e['sum'], unit)})
                footer[7] += e['sum']/12
                footer[8] += e['sum']


        footer.append('sum')
        footer.append(0)
        footer.append(0)
        savings = []
        for tag in budget.savings_tags.all():
            e = Entry.objects.filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year) & Q(tags__pk=tag.pk)).aggregate(sum=Sum('amount'))
            if e['sum']:
                savings.append({'name':tag.name.lower(), 'monthly':colorfy(e['sum']/12, unit), 'yearly':colorfy(e['sum'], unit)})
                footer[10] += e['sum']/12
                footer[11] += e['sum']

        footer = [footer]
        footer.append(['', '', '', '', '', '', '', '', '', 'total', 0, 0])
        footer.append(['', '', '', '', '', '', '', '', '', 'real', 0, 0])
        footer[1][10] = footer[0][1] + footer[0][4] + footer[0][7] + footer[0][10]
        footer[1][11] = footer[0][2] + footer[0][5] + footer[0][8] + footer[0][11]

        real = Entry.objects.exclude(category__in=ledger.accounts.values_list('category', flat=True)).filter(Q(account__in=ledger.accounts.all()) & Q(account__unit=unit) & Q(day__year=year)).aggregate(sum=Sum('amount'))['sum']
        footer[2][10] = real/12
        footer[2][11] = real

        footer[0][1] = colorfy(footer[0][1], unit)
        footer[0][2] = colorfy(footer[0][2], unit)
        footer[0][4] = colorfy(footer[0][4], unit)
        footer[0][5] = colorfy(footer[0][5], unit)
        footer[0][7] = colorfy(footer[0][7], unit)
        footer[0][8] = colorfy(footer[0][8], unit)
        footer[0][10] = colorfy(footer[0][10], unit)
        footer[0][11] = colorfy(footer[0][11], unit)
        footer[1][10] = colorfy(footer[1][10], unit)
        footer[1][11] = colorfy(footer[1][11], unit)
        footer[2][10] = colorfy(footer[2][10], unit)
        footer[2][11] = colorfy(footer[2][11], unit)


        table = []
        for i in range(max(len(income), len(consumption), len(insurance), len(savings))):
            row = []
            if i < len(income):
                row.append(income[i]['name'])
                row.append(income[i]['monthly'])
                row.append(income[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(consumption):
                row.append(consumption[i]['name'])
                row.append(consumption[i]['monthly'])
                row.append(consumption[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(insurance):
                row.append(insurance[i]['name'])
                row.append(insurance[i]['monthly'])
                row.append(insurance[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            if i < len(savings):
                row.append(savings[i]['name'])
                row.append(savings[i]['monthly'])
                row.append(savings[i]['yearly'])
            else:
                row.append('')
                row.append('')
                row.append('')
            table.append(row)
    return render(request, 'ledger/accounts/budget/budget.html', locals())

@login_required(login_url='/profile/signin/')
def edit(request):
    budget = get_object_or_404(Budget, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(instance=budget, data=request.POST)
        if form.is_valid():
            budget = form.save()
            messages.add_message(request, messages.SUCCESS, 'your budget was successfully updated.')
            return redirect('budget')
        else:
            return render(request, 'ledger/accounts/budget/form.html', locals())
    else:
        form = BudgetForm(instance=budget)
        return render(request, 'ledger/accounts/budget/form.html', locals())
    return render(request, 'ledger/accounts/budget/form.html', locals())
