# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2021 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# This file is part of ledger.
#
# ledger is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ledger is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ledger.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_protect

from ..forms import AuthenticationForm, UserChangeForm, UserCreationForm
from ..models import Budget, Ledger, Portfolio


@csrf_protect
def signin(request):
    gnext = request.GET.get("next")

    if not request.user.is_authenticated and settings.SINGLE_USER:
        login(request, get_user_model().objects.first())

    if request.user.is_authenticated:
        if not Budget.objects.filter(user=request.user).exists():
            Budget.objects.create(user=request.user)
        if not Ledger.objects.filter(user=request.user).exists():
            Ledger.objects.create(user=request.user)
        if not Portfolio.objects.filter(user=request.user).exists():
            Portfolio.objects.create(user=request.user)
        return redirect(gnext) if gnext else redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.add_message(
                        request, messages.SUCCESS, _("You have successfully signed in.")
                    )

                    return redirect(gnext) if gnext else redirect("dashboard")
                else:
                    messages.add_message(
                        request, messages.ERROR, _("Your account is disabled.")
                    )
                return redirect(request.META.get("HTTP_REFERER"))
        messages.add_message(
            request,
            messages.ERROR,
            _(
                "Please enter a correct email and password to"
                + " sign in. Note that both fields may be "
                + "case-sensitive."
            ),
        )
    else:
        form = AuthenticationForm(request)
    return render(request, "registration/signin.html", locals())


@csrf_protect
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.info(
                request,
                messages.SUCCESS,
                _("Thanks for signing up. You are now logged in."),
            )
            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, new_user)
            return redirect("users:profile")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", locals())


@method_decorator(login_required, name="dispatch")
class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    form_class = UserChangeForm
    model = get_user_model()
    success_message = _("Your profile was successfully updated.")

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        from django.urls import reverse

        return reverse("users:profile")
