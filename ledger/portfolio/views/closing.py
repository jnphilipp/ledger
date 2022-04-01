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
"""Portfolio Django app closing views."""

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..forms import ClosingForm
from ..models import Closing


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """Closing create view."""

    form_class = ClosingForm
    model = Closing
    success_message = _(
        '%(num_closings)s closings were successfully added to "%(name)s".'
    )

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return self.success_message % {
            "num_closings": len(self.object),
            "name": self.object[0].content_object.name,
        }

    def get_success_url(self):
        """Get success URL."""
        return reverse_lazy("create_another_success")
