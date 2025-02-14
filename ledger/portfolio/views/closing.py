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
"""Portfolio Django app closing views."""

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ngettext_lazy
from django.views import generic

from ..forms import ClosingForm
from ..models import Closing


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """Closing create view."""

    form_class = ClosingForm
    model = Closing
    success_message = ngettext_lazy(
        '%(num_closings)d closing were successfully added to "%(name)s".',
        '%(num_closings)d closings were successfully added to "%(name)s".',
        "num_closings",
    )

    def get_initial(self):
        """Get initial."""
        initial = {}
        if "tradeable" in self.request.GET:
            initial["tradeable"] = self.request.GET.get("tradeable")
        return initial

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {
            "num_closings": len(self.object),
            "name": self.object[0].content_object.name,
        }

    def get_success_url(self):
        """Get success URL."""
        return reverse_lazy("create_another_success")
