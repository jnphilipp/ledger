# -*- coding: utf-8 -*-

from accounts.forms import AccountForm
from accounts.models import Account
from categories.models import Category, Tag
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from ledger.dates import get_last_date_current_month
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


@method_decorator(login_required, name='dispatch')
class StatisticsView(generic.DetailView):
    model = Account
    template_name = 'accounts/account_statistics.html'

    def get_queryset(self):
        return Account.objects.filter(ledger__user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(StatisticsView, self).get_context_data(*args, **kwargs)

        if 'chart' in self.kwargs and (self.kwargs['chart'] == 'tags' or \
                self.kwargs['chart'] == 'categories'):
            context['chart'] = self.kwargs['chart']
            if context['chart'] == 'tags':
                context['chart_name'] = _('Tags')
            else:
                context['chart_name'] = _('Categories')
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
            years = context['account'].entries.dates('day', 'year')
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
            months = context['account'].entries. \
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

        if 'obj' in self.kwargs:
            obj = self.kwargs['obj']
            if context['chart'] == 'categories':
                context['category'] = get_object_or_404(Category, slug=obj)
            elif context['chart'] == 'tags':
                context['tag'] = get_object_or_404(Tag, slug=obj)
        else:
            if context['chart'] == 'categories':
                context['option_msg'] = _('Select a category')
                context['options'] = [{
                    'id': category.slug,
                    'key': 'category',
                    'value': category.name
                } for category in Category.objects.filter(
                    Q(entries__account=context['account']) &
                    Q(entries__day__year=context['year']) &
                    Q(entries__day__month=context['month'])).distinct()]
            elif context['chart'] == 'tags':
                context['option_msg'] = _('Select a tag')
                context['options'] = [{
                    'id': tag.slug,
                    'key': 'tag',
                    'value': tag.name
                } for tag in Tag.objects.filter(
                    Q(entries__account=context['account']) &
                    Q(entries__day__year=context['year']) &
                    Q(entries__day__month=context['month'])).distinct()]

        return context


@method_decorator(login_required, name='dispatch')
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = AccountForm
    model = Account
    success_message = _('The account %(name)s was successfully created.')

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

    def get_queryset(self):
        return Account.objects.filter(ledger__user=self.request.user)

    def get_success_url(self):
        msg = _('The account %(name)s was successfully deleted.')
        msg %= {'name': self.object.name}
        messages.add_message(self.request, messages.SUCCESS, msg)
        return reverse_lazy('accounts:account_list')


@method_decorator(login_required, name='dispatch')
class CloseView(generic.base.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'accounts:account_detail'

    def get_redirect_url(self, *args, **kwargs):
        ledger = get_object_or_404(Ledger, user=self.request.user)
        account = get_object_or_404(Account, slug=kwargs['slug'],
                                    ledger=ledger)
        account.closed = not account.closed
        account.save()

        if account.closed:
            msg = _('The account %(name)s was successfully closed.')
        else:
            msg = _('The account %(name)s was successfully re-open.')

        msg %= {'name': account.name}
        messages.add_message(self.request, messages.SUCCESS, msg)
        return super().get_redirect_url(*args, **kwargs)
