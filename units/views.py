# -*- coding: utf-8 -*-

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from units.forms import UnitForm
from units.models import Unit


@login_required
def list(request):
    units = Unit.objects.all()
    return render(request, 'units/unit/list.html', locals())


@login_required
def detail(request, slug):
    unit = get_object_or_404(Unit, slug=slug)
    return render(request, 'units/unit/detail.html', locals())


@login_required
@csrf_protect
def add(request):
    return _add(request, 'units/unit/form.html')


@login_required
@csrf_protect
def add_another(request):
    return _add(request, 'units/unit/add_another.html', False,
                request.GET.get('target_id'))


def _add(request, template, do_redirect=True, target_id=None):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            msg = _('The unit %(name)s was successfully created.')
            messages.add_message(request, messages.SUCCESS,
                                 msg % {'name': unit.name})
            if do_redirect:
                return redirect('units:unit', slug=unit.slug)
    else:
        form = UnitForm()
    return render(request, template, locals())


@login_required
@csrf_protect
def edit(request, slug):
    unit = get_object_or_404(Unit, slug=slug)
    if request.method == 'POST':
        form = UnitForm(instance=unit, data=request.POST)
        if form.is_valid():
            unit = form.save()
            msg = _('The unit %(name)s was successfully updated.')
            messages.add_message(request, messages.SUCCESS,
                                 msg % {'name': unit.name})
            return redirect('units:unit', slug=unit.slug)
    else:
        form = UnitForm(instance=unit)
    return render(request, 'units/unit/form.html', locals())


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

    units = Unit.objects.filter(accounts__ledger__user=request.user).distinct()
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
