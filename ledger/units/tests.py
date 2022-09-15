# -*- coding: utf-8 -*-
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:
# Copyright (C) 2014-2022 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
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

from django.test import TestCase
from units.models import Unit
from units.templatetags.units import unitformat, unitcolorfy


class TemplatetagsTestCase(TestCase):
    def test_unitformat(self):
        self.assertEquals("0.123%", unitformat(0.1234, "%.3f%%"))
        self.assertEquals("-0.123%", unitformat(-0.1234, "%.3f%%"))
        self.assertEquals("3.57 €", unitformat(3.567, "%.2f €"))
        self.assertEquals("3.57 €", unitformat(3.567, Unit.objects.get(code="EUR")))
        self.assertEquals("-3.57 €", unitformat(-3.567, Unit.objects.get(code="EUR")))
        self.assertEquals(
            "3.56734400 ₿", unitformat(3.567344, Unit.objects.get(code="BTC"))
        )

    def test_unitcolorfy(self):
        self.assertEquals(
            '<span class="green">0.123%</span>', unitcolorfy(0.1234, "%.3f%%")
        )
        self.assertEquals(
            '<span class="red">-0.123%</span>', unitcolorfy(-0.1234, "%.3f%%")
        )
        self.assertEquals(
            '<span class="green">3.57 €</span>', unitcolorfy(3.567, "%.2f €")
        )
        self.assertEquals(
            '<span class="red">-5.74 €</span>', unitcolorfy(-5.741, "%.2f €")
        )
        self.assertEquals(
            '<span class="green">3.57 €</span>',
            unitcolorfy(3.567, Unit.objects.get(code="EUR")),
        )
        self.assertEquals(
            '<span class="red">-5.74 €</span>',
            unitcolorfy(-5.741, Unit.objects.get(code="EUR")),
        )
