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

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone

from ..models import Stock, Fund


@login_required
def autocomplete(request):
    """Handels GET/POST request to autocomplete tradeables.

    GET/POST parameters:
    q --- search term
    """

    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    stocks = Stock.objects.all()
    funds = Fund.objects.all()
    if "q" in params:
        stocks = stocks.filter(name__icontains=params.pop("q")[0])
        funds = funds.filter(name__icontains=params.pop("q")[0])

    stock_content_type = ContentType.objects.get_for_model(Stock)
    fund_content_type = ContentType.objects.get_for_model(Fund)
    data = {
        "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
        "tradeable": [{"id": f"{stock_content_type.pk}{stock.pk}", "text": stock.name} for stock in stocks] + [{"id": f"{fund_content_type.pk}{fund.pk}", "text": fund.name} for fund in funds],
    }
    return JsonResponse(data)
