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

from accounts.models import Account
from categories.models import Category
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


@login_required
def categories(request, slug):
    account = get_object_or_404(Account, slug=slug, ledgers__user=request.user)

    data = {
        "xAxis": {
            "categories": [
                c.name
                for c in Category.objects.filter(
                    id__in=account.entries.values_list("category", flat=True)
                ).distinct()
            ],
            "title": {"text": str(_("Categories"))},
        },
        "yAxis": {"title": {"text": str(_("Number of times used"))}},
        "series": [
            {
                "name": "entries",
                "data": [
                    [c.name, c.count]
                    for c in Category.objects.filter(
                        id__in=account.entries.values_list("category", flat=True)
                    )
                    .extra(
                        select={
                            "count": "SELECT COUNT(*) FROM accounts_entry WHERE accounts_entry.category_id=categories_category.id AND accounts_entry.account_id=%s"
                        },
                        select_params=(account.id,),
                    )
                    .distinct()
                ],
            }
        ],
    }
    return JsonResponse(data)
