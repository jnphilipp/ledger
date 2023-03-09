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
"""Ledger Django app file views."""

from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..models import File
from ..forms import FileForm


class DetailView(generic.DetailView):
    """File detail view."""

    model = File

    def render_to_response(self, context, **response_kwargs):
        """Render to response."""
        return FileResponse(open(self.object.file.path, "rb"), as_attachment=True)


class CreateView(SuccessMessageMixin, generic.edit.CreateView):
    """File create view."""

    form_class = FileForm
    model = File
    success_url = reverse_lazy("create_another_success")

    def get_initial(self):
        """Get initital."""
        return {
            "content_type": self.kwargs["content_type"],
            "object_id": self.kwargs["object_id"],
        }

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _(
            'The file "%(name)s" was successfully uploaded and added to "%(related)s".'
        ) % {"name": self.object.name, "related": self.object.content_object}


class UpdateView(SuccessMessageMixin, generic.edit.UpdateView):
    """File update view."""

    form_class = FileForm
    model = File
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The file "%(name)s" was successfully updated.') % {
            "name": self.object.name
        }


class DeleteView(SuccessMessageMixin, generic.edit.DeleteView):
    """File delete view."""

    model = File
    success_url = reverse_lazy("create_another_success")

    def get_success_message(self, cleaned_data):
        """Get success message."""
        return _('The file "%(name)s" was successfully deleted.') % {
            "name": self.object.name
        }
