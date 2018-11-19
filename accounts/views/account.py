# -*- coding: utf-8 -*-

from accounts.forms import AccountForm
from accounts.models import Account
from categories.models import Category, Tag
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from ledger.functions.dates import get_last_date_current_month
from users.models import Ledger


@method_decorator(login_required, name='dispatch')
class ListView(generic.ListView):
    context_object_name = 'accounts'
    model = Account

    def get_queryset(self):
        return Account.objects.filter(ledger__user=self.request.user)


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Account

    def get_queryset(self):
        return Account.objects.filter(ledger__user=self.request.user)

    def get_template_names(self):
        if 'statements' in self.request.path:
            return 'accounts/account_statement_list.html'
        return 'accounts/account_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context['o'] = '-updated_at'
        if 'o' in self.request.GET:
            context['o'] = self.request.GET.get('o')

        if 'statements' in self.request.path:
            context['statements'] = context['account'].statements. \
                order_by(context['o'])
        else:
            context['entries'] = context['account'].entries. \
                filter(day__lte=get_last_date_current_month()).reverse()[:20]
            context['statements'] = context['account'].statements. \
                order_by(context['o'])[:20]
        return context


@login_required
def statistics(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    chart = request.GET.get('chart')
    year = request.GET.get('year')
    month = request.GET.get('month')
    category = get_object_or_404(Category, slug=request.GET.get('category')) if request.GET.get('category') else None
    tag = get_object_or_404(Tag, slug=request.GET.get('tag')) if request.GET.get('tag') else None

    if year and month:
        month_name = date(year=int(year), month=int(month), day=1).strftime('%B')

    options = []
    if not chart:
        option_msg = _('Select a chart')
        options = [{
            'id': 'categories',
            'key': 'chart',
            'value': _('Categories')
        },
        {
            'id': 'tags',
            'key': 'chart',
            'value': _('Tags')
        }]
    elif chart and not year:
        years = account.entries.dates('day', 'year')
        if chart == 'tags':
            chart_name = _('Tags')
            years = years.filter(tags__isnull=False)
        else:
            chart_name = _('Categories')

        option_msg = _('Select a year')
        option_name = 'year'
        options = [{
            'id': year.strftime('%Y'),
            'key': 'year',
            'value': year.strftime('%Y')
        } for year in years]
    elif chart and year and not month:
        months = account.entries.filter(day__year=year).dates('day', 'month')
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
    elif chart and year and month and not category and not tag:
        if chart == 'categories':
            chart_name = _('Categories')
            option_msg = _('Select a category')
            options = [{
                'id': category.slug,
                'key': 'category',
                'value': category.name
            } for category in Category.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
        elif chart == 'tags':
            chart_name = _('Tags')
            option_msg = _('Select a tag')
            options = [{
                'id': tag.slug,
                'key': 'tag',
                'value': tag.name
            } for tag in Tag.objects.filter(Q(entries__account=account) & Q(entries__day__year=year) & Q(entries__day__month=month)).distinct()]
    else:
        chart_name = _('Tags') if chart == 'tags' else _('Categories')
    return render(request, 'accounts/account/statistics.html', locals())


@method_decorator(login_required, name='dispatch')
class CreateView(generic.edit.CreateView):
    form_class = AccountForm
    model = Account
    success_message =_('The account %(name)s was successfully created.')

    def get_initial(self):
        return {'ledger': self.request.user.ledger}

    def form_valid(self, form):
        r = super(CreateView, self).form_valid(form)
        self.request.user.ledger.accounts.add(self.object)
        self.request.user.ledger.save()
        return r


@method_decorator(login_required, name='dispatch')
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = AccountForm
    model = Account
    success_message = _('The account %(name)s was successfully updated.')

    def get_queryset(self):
        return Account.objects.filter(ledger__user=self.request.user)


@method_decorator(login_required, name='dispatch')
class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    model = Account
    success_url = reverse_lazy('accounts:account_list')
    success_message = _('The account %(name)s was successfully deleted.')

    def get_queryset(self):
        return Account.objects.filter(ledger__user=self.request.user)


@login_required
def close(request, slug):
    ledger = get_object_or_404(Ledger, user=request.user)
    account = get_object_or_404(Account, slug=slug, ledger=ledger)
    account.closed = not account.closed
    account.save()
    if account.closed:
        messages.add_message(request, messages.SUCCESS, _('The account %(name)s was successfully closed.') % {'name': account.name})
    else:
        messages.add_message(request, messages.SUCCESS, _('The account %(name)s was successfully re-open.') % {'name': account.name})
    return redirect('accounts:account', slug=account.slug)



