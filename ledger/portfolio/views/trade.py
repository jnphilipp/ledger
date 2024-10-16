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
"""Portfolio Django app trade views."""

from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..forms import TradeForm
from ..models import Position, Trade


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """Trade create view."""

    form_class = TradeForm
    model = Trade
    success_message = _('The trade "%(name)s" was successfully created.')

    def get_initial(self):
        """Get initial."""
        initial = {}
        if "position" in self.request.GET:
            initial["position"] = get_object_or_404(
                Position, slug=self.request.GET.get("position")
            )
        return initial

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {
            "name": f"{self.object.position} - #{self.object.pk}"
        }

    def get_success_url(self):
        """Get success URL."""
        return (
            reverse_lazy("create_another_success")
            + "?next="
            + reverse_lazy(
                "portfolio:position_detail", kwargs={"slug": self.object.position.slug}
            )
        )


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """Trade update view."""

    form_class = TradeForm
    model = Trade
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""

        return _('The trade "%(name)s" was successfully updated.') % {
            "name": f"{self.object.position} - #{self.object.pk}"
        }


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    """Trade delete view."""

    model = Trade
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The trade #"%(name)s" was successfully deleted.') % {
            "name": f"{self.object.position} - #{self.object.pk}"
        }
