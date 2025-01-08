# Copyright (C) 2014-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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
"""Ledger Django app base views."""

import json

from django.db.models import Count
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from units.models import Unit

from ..models import Account, Category, Tag


class AnotherSuccessView(TemplateView):
    """Another success view."""

    template_name = "ledger/another_success.html"

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super().get_context_data(*args, **kwargs)
        if "next" in self.request.GET:
            context["next"] = self.request.GET.get("next")

        return context


def choices_autocomplete(request):
    """Handels GET/POST request to autocomplete accounts.

    GET/POST parameters:
    q --- search term
    """

    params = request.POST.copy() if request.method == "POST" else request.GET.copy()
    if "application/json" == request.META.get("CONTENT_TYPE"):
        params.update(json.loads(request.body.decode("utf-8")))

    accounts = Account.objects.annotate(Count("entries")).order_by("-entries__count")
    categories = Category.objects.annotate(Count("entries")).order_by("-entries__count")
    tags = Tag.objects.annotate(Count("entries")).order_by("-entries__count")
    units = Unit.objects.annotate(Count("accounts")).order_by("-accounts__count")
    if "q" in params:
        q = params.pop("q")[0]
        accounts = accounts.filter(name__icontains=q)
        categories = categories.filter(name__icontains=q)
        tags = tags.filter(name__icontains=q)
        units = units.filter(name__icontains=q)

    data = {
        "response_date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S:%f%z"),
        "choices": [
            {
                "text": _("Accounts"),
                "children": [
                    {"id": f"a{account.id}", "text": account.name}
                    for account in accounts
                ],
            }
        ]
        + [
            {
                "text": _("Categories"),
                "children": [
                    {"id": f"c{category.id}", "text": category.name}
                    for category in categories
                ],
            }
        ]
        + [
            {
                "text": _("Tags"),
                "children": [{"id": f"t{tag.id}", "text": tag.name} for tag in tags],
            }
        ]
        + [
            {
                "text": _("Units"),
                "children": [
                    {"id": f"u{unit.id}", "text": unit.name} for unit in units
                ],
            }
        ],
    }
    return JsonResponse(data)
