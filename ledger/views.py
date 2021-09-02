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

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic


@method_decorator(login_required, name="dispatch")
class AnotherSuccessView(generic.base.TemplateView):
    template_name = "ledger/another_success.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AnotherSuccessView, self).get_context_data(*args, **kwargs)
        if "reload" in self.request.GET:
            context["reload"] = bool(self.request.GET.get("reload"))
        else:
            context["reload"] = False
        if "next" in self.request.GET:
            context["next"] = self.request.GET.get("next")
        if "target_id" in self.request.GET:
            context["target_id"] = self.request.GET.get("target_id")
        if "value" in self.request.GET:
            context["value"] = self.request.GET.get("value")
        if "name" in self.request.GET:
            context["name"] = self.request.GET.get("name")

        return context
