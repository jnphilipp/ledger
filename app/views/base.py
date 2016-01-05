# -*- coding: utf-8 -*-

from app.forms import AuthenticationForm
from app.models import Ledger
from django.contrib import messages
from django.contrib.auth import authenticate, login, views
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def signin(request):
    gnext = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 'you have successfully logged in.')

                try:
                    Ledger.objects.get(user=user)
                except Ledger.DoesNotExist:
                    Ledger.objects.create(user=user)

                return redirect(gnext) if gnext else redirect('dashboard')
            else:
                messages.add_message(request, messages.ERROR, 'your account is disabled.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.add_message(request, messages.ERROR, 'please enter the correct username and password for an account. note that both fields may be case-sensitive.')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = AuthenticationForm(request)
        return render(request, 'registration/login.html', locals())

@csrf_protect
def password_reset(request):
    return views.password_reset(request, post_reset_redirect=reverse('signin'))

@csrf_protect
def password_reset_confirm(request, uidb64=None, token=None):
    return views.password_reset_confirm(request, uidb64=uidb64, token=token, post_reset_redirect=reverse('signin'))
