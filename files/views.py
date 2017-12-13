# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from files.forms import FileForm
from files.models import File
from users.models import Ledger


@login_required
def detail(request, slug):
    file = get_object_or_404(File, slug=slug)
    ledger = get_object_or_404(Ledger, user=request.user)

    if ContentType.objects.get_for_model(Account) == file.content_type:
        if ledger.accounts.filter(pk=file.object_id).exists():
            return redirect(file.file.url)
    elif ContentType.objects.get_for_model(Entry) == file.content_type:
        if ledger.accounts.filter(pk=file.content_object.account.pk).exists():
            return redirect(file.file.url)
    elif file.uploader == request.user:
        return redirect(file.file.url)
    return HttpResponseForbidden()


@login_required
@csrf_protect
def add(request, content_type, object_id):
    return _add(request, content_type, object_id, 'files/file/form.html',
                a=request.GET.get('a'))


@login_required
@csrf_protect
def add_another(request, content_type, object_id):
    print(request.GET.get('a'))
    return _add(request, content_type, object_id,
                'files/file/another_form.html', True, request.GET.get('a'))


def _add(request, content_type, object_id, template, do_reload=False, a='t'):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            messages.add_message(request, messages.SUCCESS,
                                 _('The file "%(name)s" was successfully ' +
                                   'uploaded.') % {'name': file.name})
            if not do_reload:
                if ContentType.objects.get_for_model(Account) == file.content_type:
                    return redirect('accounts:account_statements',
                                    slug=file.content_object.slug)
                elif ContentType.objects.get_for_model(Entry) == file.content_type:
                    if a == 't' or a is None:
                        return redirect('accounts:account_entry',
                                        slug=file.content_object.account.slug,
                                        entry_id=file.content_object.pk)
                    else:
                        return redirect('accounts:entry',
                                        entry_id=file.content_object.pk)
                else:
                    return redirect('files:edit', slug=file.slug)
    else:
        form = FileForm(initial={
            'uploader': request.user,
            'content_type': ContentType.objects.get_for_id(content_type),
            'object_id': object_id
        })
    return render(request, template, locals())


@login_required
@csrf_protect
def delete(request, slug):
    file = get_object_or_404(File, slug=slug)
    if file.uploader == request.user:
        if request.method == 'POST':
            file.delete()
            messages.add_message(request, messages.SUCCESS,
                                 _('The file "%(name)s" was successfully ' +
                                   'deleted.') % {'name': file.name})
            if ContentType.objects.get_for_model(Account) == file.content_type:
                return redirect('accounts:account_statements',
                                slug=file.content_object.slug)
            elif ContentType.objects.get_for_model(Entry) == file.content_type:
                return redirect('accounts:account_entry',
                                slug=file.content_object.account.slug,
                                entry_id=file.content_object.pk)
            else:
                return redirect('files:edit', slug=file.slug)
        return render(request, 'files/file/delete.html', locals())
    else:
        return HttpResponseForbidden()


@login_required
@csrf_protect
def edit(request, slug):
    file = get_object_or_404(File, slug=slug)
    if file.uploader == request.user:
        if request.method == 'POST':
            form = FileForm(request.POST, request.FILES, instance=file)
            if form.is_valid():
                file = form.save()
                messages.add_message(request, messages.SUCCESS,
                                     _('The file "%(name)s" was successfully ' +
                                       'updated.') % {'name': file.name})
                if ContentType.objects.get_for_model(Account) == file.content_type:
                    return redirect('accounts:account_statements',
                                    slug=file.content_object.slug)
                elif ContentType.objects.get_for_model(Entry) == file.content_type:
                    return redirect('accounts:account_entry',
                                    slug=file.content_object.account.slug,
                                    entry_id=file.content_object.pk)
                else:
                    return redirect('files:edit', slug=file.slug)
        else:
            form = FileForm(instance=file)
        return render(request, 'files/file/form.html', locals())
    else:
        return HttpResponseForbidden()
