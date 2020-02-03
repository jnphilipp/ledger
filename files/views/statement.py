# -*- coding: utf-8 -*-

from accounts.models import Account
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from files.forms import StatementFilterForm, StatementForm
from files.models import Statement


@method_decorator(login_required, name='dispatch')
class ListView(generic.ListView):
    context_object_name = 'statements'
    model = Statement
    paginate_by = 200

    def get_queryset(self):
        self.form = StatementFilterForm(self.request.GET)
        self.o = '-updated_at'
        if 'o' in self.request.GET:
            self.o = self.request.GET.get('o')

        statements = Statement.objects.filter(
            account__ledger__user=self.request.user)

        self.accounts = []
        if self.form.is_valid():
            if 'accounts' in self.form.cleaned_data and \
                    self.form.cleaned_data['accounts']:
                self.accounts = [a.pk for a in
                                 self.form.cleaned_data['accounts']]
                statements = statements.filter(account__in=self.accounts)

        return statements.order_by(self.o)

    def get_context_data(self, *args, **kwargs):
        context = super(ListView, self).get_context_data(*args, **kwargs)
        context['form'] = self.form
        context['accounts'] = self.accounts
        context['o'] = self.o
        return context


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Statement

    def get_queryset(self):
        return Statement.objects.filter(
            account__ledger__user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        return FileResponse(open(self.object.file.path, 'rb'),
                            as_attachment=True)


@method_decorator(login_required, name='dispatch')
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = StatementForm
    model = Statement
    success_message = _('The statement "%(name)s" was successfully uploaded.')

    def get_initial(self):
        initial = {'uploader': self.request.user}
        if 'slug' in self.kwargs:
            initial['account'] = get_object_or_404(Account,
                                                   slug=self.kwargs['slug'])
        return initial

    def get_success_url(self):
        url = reverse_lazy('create_another_success')
        if 'reload' in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        elif 'target_id' in self.request.GET:
            url = f'{url}?target_id={self.request.GET.get("target_id")}&' + \
                f'value={self.object.pk}&name={self.object.name}'
        return url


@method_decorator(login_required, name='dispatch')
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = StatementForm
    model = Statement
    success_message = _('The statement "%(name)s" was successfully updated.')

    def get_queryset(self):
        return Statement.objects.filter(uploader=self.request.user)

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
    model = Statement

    def get_queryset(self):
        return Statement.objects.filter(uploader=self.request.user)

    def get_success_url(self):
        msg = _('The statement "%(name)s" was successfully deleted.')
        msg %= {'name': self.object.name}
        messages.add_message(self.request, messages.SUCCESS, msg)

        url = reverse_lazy('create_another_success')
        if 'reload' in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        elif 'target_id' in self.request.GET:
            url = f'{url}?target_id={self.request.GET.get("target_id")}&' + \
                f'value={self.object.pk}&name={self.object.name}'
        return url
