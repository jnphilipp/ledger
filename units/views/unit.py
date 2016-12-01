# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
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
    return _add(request, 'units/unit/add_another.html', False, request.GET.get('target_id'))


def _add(request, template, do_redirect=True, target_id=None):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.add_message(request, messages.SUCCESS, _('the unit %(name)s was successfully created.' % {'name': unit.name.lower()}))
            if do_redirect:
                return redirect('unit', slug=unit.slug)
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
            messages.add_message(request, messages.SUCCESS, _('the unit %(name)s was successfully updated.') % {'name': unit.name.lower()})
            return redirect('unit', slug=unit.slug)
    else:
        form = UnitForm(instance=unit)
    return render(request, 'units/unit/form.html', locals())
