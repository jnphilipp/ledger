# -*- coding: utf-8 -*-

from categories.forms import CategoryForm
from categories.models import Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Func, Q
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic


@method_decorator(login_required, name='dispatch')
class ListView(generic.ListView):
    context_object_name = 'categories'
    model = Category

    def get_queryset(self):
        return Category.objects.filter(
            Q(entries__account__ledger__user=self.request.user) |
            Q(accounts__ledger__user=self.request.user)).annotate(
            lname=Func(F('name'), function='LOWER')).distinct(). \
            order_by('lname')


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context['entry_list'] = context['category'].entries.filter(
            account__ledger__user=self.request.user)

        if 'year' not in self.kwargs:
            years = context['category'].entries.filter(
                account__ledger__user=self.request.user).dates('day', 'year')
            context['years'] = [y.strftime('%Y') for y in years]
        else:
            context['year'] = self.kwargs['year']

        return context

    def get_queryset(self):
        return Category.objects.filter(
            Q(entries__account__ledger__user=self.request.user) |
            Q(accounts__ledger__user=self.request.user)).distinct()


@method_decorator(login_required, name='dispatch')
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = CategoryForm
    model = Category
    success_message = _('The category "%(name)s" was successfully updated.')

    def get_queryset(self):
        return Category.objects.filter(
            Q(entries__account__ledger__user=self.request.user) |
            Q(accounts__ledger__user=self.request.user)).distinct()

    def get_success_url(self):
        url = reverse_lazy('create_another_success')
        if 'reload' in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        elif 'target_id' in self.request.GET:
            url = f'{url}?target_id={self.request.GET.get("target_id")}&' + \
                f'value={self.object.pk}&name={self.object.name}'
        return url


@method_decorator(login_required, name='dispatch')
class DeleteView(generic.edit.DeleteView):
    model = Category

    def get_queryset(self):
        return Category.objects.filter(
            Q(entries__account__ledger__user=self.request.user) |
            Q(accounts__ledger__user=self.request.user)).distinct()

    def get_success_url(self):
        msg = _('The category "%(name)s" was successfully deleted.')
        messages.add_message(self.request, messages.SUCCESS,
                             msg % {'name': self.object.name})

        url = reverse_lazy('create_another_success')
        if 'reload' in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}&next=' + \
                f'{reverse_lazy("categories:category_list")}'
        elif 'target_id' in self.request.GET:
            url = f'{url}?target_id={self.request.GET.get("target_id")}&' + \
                f'value={self.object.pk}&name={self.object.name}'
        return url
