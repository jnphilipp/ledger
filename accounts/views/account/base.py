# -*- coding: utf-8 -*-

from accounts.forms import AccountForm
from accounts.models import Account
from categories.models import Category, Tag
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Q
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

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)

        if 'categories_year' not in self.kwargs:
            years = context['account'].entries.dates('day', 'year')
            context['categories_years'] = [y.strftime('%Y') for y in years]
        else:
            context['categories_year'] = self.kwargs['categories_year']

        if 'categories_month' not in self.kwargs and \
                'categories_year' in self.kwargs:
            months = context['account'].entries.filter(
                day__year=context['categories_year']).dates('day', 'month')
            context['categories_months'] = [
                (m.strftime('%m'), m.strftime('%B')) for m in months]
        elif 'categories_month' in self.kwargs:
            context['categories_month'] = self.kwargs['categories_month']

        if 'tags_year' not in self.kwargs:
            years = context['account'].entries.filter(tags__isnull=False). \
                dates('day', 'year')
            context['tags_years'] = [y.strftime('%Y') for y in years]
        else:
            context['tags_year'] = self.kwargs['tags_year']

        if 'tags_month' not in self.kwargs and 'tags_year' in self.kwargs:
            months = context['account'].entries.filter(tags__isnull=False). \
                filter(day__year=context['tags_year']).dates('day', 'month')
            context['tags_months'] = [
                (m.strftime('%m'), m.strftime('%B')) for m in months]
        elif 'tags_month' in self.kwargs:
            context['tags_month'] = self.kwargs['tags_month']

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
