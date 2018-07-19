# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth import authenticate, login, views
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from ..forms import (AuthenticationForm, PasswordChangeForm,
                     SetPasswordForm, UserCreationForm)
from ..models import Budget, Ledger


@csrf_protect
def signin(request):
    gnext = request.GET.get('next')

    if request.user.is_authenticated:
        return redirect(gnext) if gnext else redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.add_message(request, messages.SUCCESS,
                                         _('You have successfully signed in.'))

                    return redirect(gnext) if gnext else redirect('dashboard')
                else:
                    messages.add_message(request, messages.ERROR,
                                         _('Your account is disabled.'))
                return redirect(request.META.get('HTTP_REFERER'))
        messages.add_message(request, messages.ERROR,
                             _('Please enter a correct email and password to' +
                               ' sign in. Note that both fields may be ' +
                               'case-sensitive.'))
    else:
        form = AuthenticationForm(request)
    return render(request, 'registration/signin.html', locals())


@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            Ledger.objects.create(user=new_user)
            Budget.objects.create(user=new_user)
            messages.info(request, messages.SUCCESS,
                          _('Thanks for signing up. You are now logged in.'))
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect('users:profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', locals())


@csrf_protect
def signout(request):
    return views.logout(request, template_name='registration/signout.html')


@csrf_protect
def password_change(request):
    done_url = reverse('users:password_change_done')
    return views.password_change(request,
                                 password_change_form=PasswordChangeForm,
                                 post_change_redirect=done_url)


@csrf_protect
def password_change_done(request):
    return views.password_change_done(request)


@csrf_protect
def password_reset(request):
    done_url = reverse('users:password_reset_done')
    return views.password_reset(request, password_reset_form=PasswordResetForm,
                                post_reset_redirect=done_url)


@csrf_protect
def password_reset_done(request):
    return views.password_reset_done(request)


@csrf_protect
def password_reset_confirm(request, uidb64=None, token=None):
    complete_url = reverse('users:password_reset_complete')
    return views.password_reset_confirm(request, uidb64=uidb64, token=token,
                                        set_password_form=SetPasswordForm,
                                        post_reset_redirect=complete_url)


@csrf_protect
def password_reset_complete(request):
    return views.password_reset_complete(request)
