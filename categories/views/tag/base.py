# -*- coding: utf-8 -*-

from categories.forms import TagForm
from categories.models import Tag
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic


@method_decorator(login_required, name='dispatch')
class ListView(generic.ListView):
    context_object_name = 'tags'
    model = Tag

    def get_queryset(self):
        return Tag.objects.filter(
            entries__account__ledger__user=self.request.user).distinct().extra(
                select={'lname': 'lower(categories_tag.name)'}
            ).order_by('lname')


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Tag

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context['entry_list'] = context['tag'].entries.filter(
            account__ledger__user=self.request.user)

        if 'year' not in self.kwargs:
            years = context['tag'].entries.filter(
                account__ledger__user=self.request.user).dates('day', 'year')
            context['years'] = [y.strftime('%Y') for y in years]
        else:
            context['year'] = self.kwargs['year']

        return context


@method_decorator(login_required, name='dispatch')
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = TagForm
    model = Tag
    success_message = _('The tag "%(name)s" was successfully created.')

    def get_template_names(self):
        if 'another' in self.request.path:
            return 'categories/tag_another_form.html'
        return 'categories/tag_form.html'

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
        else:
            return reverse_lazy('categories:tag_detail',
                                args=[self.object.slug])


@method_decorator(login_required, name='dispatch')
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = TagForm
    model = Tag
    success_message = _('The tag "%(name)s" was successfully updated.')

    def get_queryset(self):
        return Tag.objects.filter(
            entries__account__ledger__user=self.request.user).distinct()


@method_decorator(login_required, name='dispatch')
class DeleteView(generic.edit.DeleteView):
    model = Tag

    def get_queryset(self):
        return Tag.objects.filter(
            entries__account__ledger__user=self.request.user).distinct()

    def get_success_url(self):
        msg = _('The tag "%(name)s" was successfully deleted.')
        messages.add_message(self.request, messages.SUCCESS,
                             msg % {'name': self.object.name})
        return reverse_lazy('categories:tag_list')
