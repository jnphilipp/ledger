# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2023 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Units Django app views."""

import json

from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone

from .models import Unit


def autocomplete(request):
    """Handels GET/POST request to autocomplete units.

    GET/POST parameters:
    q --- search term
    """

    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    units = Unit.objects.annotate(Count("accounts")).order_by("-accounts__count")
    if "q" in params:
        q = params.pop("q")[0]
        units = units.filter(Q(name__icontains=q) | Q(code__icontains=q))

    data = {
        "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
        "units": [{"id": unit.id, "text": unit.name} for unit in units],
    }
    return JsonResponse(data)
