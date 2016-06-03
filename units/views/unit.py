# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from units.forms import UnitForm
from units.models import Unit


@login_required(login_url='/users/signin/')
def units(request):
    units = Unit.objects.all()
    return render(request, 'units/units.html', locals())


@login_required(login_url='/users/signin/')
def unit(request, slug):
    unit = get_object_or_404(Unit, slug=slug)
    return render(request, 'units/unit.html', locals())


@login_required(login_url='/users/signin/')
@csrf_protect
def add(request):
    return _add(request, 'units/add.html')


@login_required(login_url='/users/signin/')
@csrf_protect
def add_another(request):
    return _add(request, 'units/add_another.html', False)


def _add(request, template, do_redirect=True):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.add_message(request, messages.SUCCESS, _('the unit %(name)s was successfully created.' % {'name': unit.name.lower()}))
            if do_redirect:
                return redirect('unit', slug=unit.slug)
        return render(request, template, locals())
    else:
        form = UnitForm()
        return render(request, template, locals())


@login_required(login_url='/users/signin/')
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
            return render(request, 'units/edit.html', locals())
    else:
        form = UnitForm(instance=unit)
        return render(request, 'units/edit.html', locals())
