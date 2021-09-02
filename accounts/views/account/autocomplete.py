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

import json

from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone


@login_required
def autocomplete(request):
    """Handels GET/POST request to autocomplete accounts.

    GET/POST parameters:
    q --- search term
    """

    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    accounts = (
        Account.objects.filter(ledger__user=request.user)
        .annotate(Count("entries"))
        .order_by("-entries__count")
    )
    if "q" in params:
        accounts = accounts.filter(name__icontains=params.pop("q")[0])
    if "closed" in params:
        closed = True if params.pop("closed")[0].lower() == "true" else False
        accounts = accounts.filter(closed=closed)

    data = {
        "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
        "accounts": [{"id": account.id, "text": account.name} for account in accounts],
    }
    return JsonResponse(data)
