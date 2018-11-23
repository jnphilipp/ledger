# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import FileResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from files.forms import FileForm
from files.models import File


account_type = ContentType.objects.get_for_model(Account)
entry_type = ContentType.objects.get_for_model(Entry)


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = File

    def get_queryset(self):
        return File.objects.filter(
            Q(accounts__ledger__user=self.request.user) |
            Q(entries__account__ledger__user=self.request.user))

    def render_to_response(self, context, **response_kwargs):
        return FileResponse(open(self.object.file.path, 'rb'),
                            as_attachment=True)


@method_decorator(login_required, name='dispatch')
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = FileForm
    model = File
    success_message = _('The file "%(name)s" was successfully uploaded.')

    def get_initial(self):
        ctype = ContentType.objects.get_for_id(self.kwargs['content_type'])
        return {'uploader': self.request.user,
                'content_type': ctype,
                'object_id': self.kwargs['object_id']}

    def get_template_names(self):
        if 'another' in self.request.path:
            return 'files/file_another_form.html'
        return 'files/file_form.html'

    def get_success_url(self):
        if 'another' in self.request.path:
            url = reverse_lazy('create_another_success')
            if 'reload' in self.request.GET:
                url = '%s?reload=%s' % (url, self.request.GET.get('reload'))
            elif 'target_id' in self.request.GET:
                url = '%s?target_id=%s&value=%s&name=%s' % (
                    url, self.request.GET.get('target_id'), self.object.pk,
                    self.object.name)
            return url
        elif self.object.content_type == account_type:
            return reverse_lazy('accounts:account_statement_list',
                                args=[self.object.content_object.slug])
        elif self.object.content_type == entry_type:
            return reverse_lazy('accounts:account_entry_detail',
                                args=[self.object.content_object.account.slug,
                                      self.object.content_object.pk])
        else:
            return reverse_lazy('files:edit', args=[self.object.slug])


@method_decorator(login_required, name='dispatch')
class DeleteView(generic.edit.DeleteView):
    model = File

    def get_queryset(self):
        return File.objects.filter(uploader=self.request.user)

    def get_success_url(self):
        msg = _('The file "%(name)s" was successfully deleted.')
        msg %= {'name': self.object.name}
        messages.add_message(self.request, messages.SUCCESS, msg)

        if self.object.content_type == account_type:
            return reverse_lazy('accounts:account_statement_list',
                                args=[self.object.content_object.slug])
        elif self.object.content_type == entry_type:
            return reverse_lazy('accounts:account_entry_detail',
                                args=[self.object.content_object.account.slug,
                                      self.object.content_object.pk])
        else:
            return reverse_lazy('files:edit', args=[self.object.slug])


@method_decorator(login_required, name='dispatch')
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = FileForm
    model = File
    success_message = _('The file "%(name)s" was successfully updated.')

    def get_queryset(self):
        return File.objects.filter(uploader=self.request.user)

    def get_success_url(self):
        if self.object.content_type == account_type:
            return reverse_lazy('accounts:account_statement_list',
                                args=[self.object.content_object.slug])
        elif self.object.content_type == entry_type:
            return reverse_lazy('accounts:account_entry_detail',
                                args=[self.object.content_object.account.slug,
                                      self.object.content_object.pk])
        else:
            return reverse_lazy('files:edit', args=[self.object.slug])
