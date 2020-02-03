# -*- coding: utf-8 -*-

from accounts.models import Entry
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from files.forms import InvoiceForm
from files.models import Invoice


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Invoice

    def get_queryset(self):
        return Invoice.objects.filter(
            entry__account__ledger__user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        return FileResponse(open(self.object.file.path, 'rb'),
                            as_attachment=True)


@method_decorator(login_required, name='dispatch')
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = InvoiceForm
    model = Invoice
    success_message = _('The invoice "%(name)s" was successfully uploaded.')

    def get_initial(self):
        entry = get_object_or_404(Entry, pk=self.kwargs['entry'])
        return {'uploader': self.request.user, 'entry': entry}

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
    form_class = InvoiceForm
    model = Invoice
    success_message = _('The invoice "%(name)s" was successfully updated.')

    def get_queryset(self):
        return Invoice.objects.filter(uploader=self.request.user)

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
    model = Invoice

    def get_queryset(self):
        return Invoice.objects.filter(uploader=self.request.user)

    def get_success_url(self):
        msg = _('The invoice "%(name)s" was successfully deleted.')
        msg %= {'name': self.object.name}
        messages.add_message(self.request, messages.SUCCESS, msg)

        url = reverse_lazy('create_another_success')
        if 'reload' in self.request.GET:
            url = f'{url}?reload={self.request.GET.get("reload")}'
        elif 'target_id' in self.request.GET:
            url = f'{url}?target_id={self.request.GET.get("target_id")}&' + \
                f'value={self.object.pk}&name={self.object.name}'
        return url
