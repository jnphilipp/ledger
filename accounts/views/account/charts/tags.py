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
from categories.models import Tag
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


def tags(request, slug):
    account = get_object_or_404(Account, slug=slug)

    data = {
        "xAxis": {
            "categories": [
                t.name
                for t in Tag.objects.filter(
                    id__in=account.entries.values_list("tags", flat=True)
                ).distinct()
            ],
            "title": {"text": str(_("Tags"))},
        },
        "yAxis": {"title": {"text": str(_("Number of times used"))}},
        "series": [
            {
                "name": "entries",
                "data": [
                    [t.name, t.count]
                    for t in Tag.objects.filter(
                        id__in=account.entries.values_list("tags", flat=True)
                    )
                    .extra(
                        select={
                            "count": "SELECT COUNT(*) FROM accounts_entry JOIN accounts_entry_tags ON accounts_entry.id=accounts_entry_tags.entry_id WHERE accounts_entry_tags.tag_id=categories_tag.id AND accounts_entry.account_id=%s"
                        },
                        select_params=(account.id,),
                    )
                    .distinct()
                ],
            }
        ],
    }
    return JsonResponse(data)
