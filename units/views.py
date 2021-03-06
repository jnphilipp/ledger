# -*- coding: utf-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import UnitForm
from .models import Unit


@method_decorator(login_required, name='dispatch')
class ListView(generic.ListView):
    context_object_name = 'units'
    model = Unit


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Unit


@method_decorator(login_required, name='dispatch')
class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    form_class = UnitForm
    model = Unit
    success_message = _('The unit "%(name)s" was successfully created.')

    def get_template_names(self):
        if 'another' in self.request.path:
            return 'units/unit_another_form.html'
        return 'units/unit_form.html'

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
            return reverse_lazy('units:detail', args=[self.object.slug])


@method_decorator(login_required, name='dispatch')
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = UnitForm
    model = Unit
    success_message = _('The unit %(name)s was successfully updated.')


@login_required
def autocomplete(request):
    """Handels GET/POST request to autocomplete units.

    GET/POST parameters:
    q --- search term
    """

    params = request.POST.copy() if request.method == 'POST' \
        else request.GET.copy()
    if 'application/json' == request.META.get('CONTENT_TYPE'):
        params.update(json.loads(request.body.decode('utf-8')))

    units = Unit.objects.filter(accounts__ledger__user=request.user). \
        distinct().annotate(Count('accounts')).order_by('-accounts__count')
    if 'q' in params:
        units = units.filter(name__icontains=params.pop('q')[0])

    data = {
        'response_date': timezone.now().strftime('%Y-%m-%dT%H:%M:%S:%f%z'),
        'units': [{
            'id': unit.id,
            'text': unit.name
        } for unit in units]
    }
    return JsonResponse(data)
