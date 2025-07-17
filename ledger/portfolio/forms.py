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
"""Portfolio Django app forms."""


from datetime import datetime
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Closing, ETF, Fund, Position, Stock, Trade, Tradeable
from .settings import (
    CLOSING_FORM_DATEFORMAT,
    CLOSING_FORM_INITIAL_DATE_FIELD,
    CLOSING_FORM_INITIAL_PRICE_FIELD,
    CLOSING_FORM_INITIAL_LOW_FIELD,
    CLOSING_FORM_INITIAL_HIGH_FIELD,
)


class TradeableForm(forms.ModelForm):
    """Tradeable model form."""

    type = forms.ChoiceField(
        choices=[(None, ""), (0, _("ETF")), (1, _("Fund")), (2, _("Stock"))],
    )

    def __init__(self, *args, **kwargs):
        """Init."""
        if "initial" in kwargs and kwargs["initial"]:
            if isinstance(kwargs["initial"], ETF):
                self._meta.model = ETF
            elif isinstance(kwargs["initial"], Fund):
                self._meta.model = Fund
            elif isinstance(kwargs["initial"], Stock):
                self._meta.model = Stock
        else:
            self._meta.model = ETF
        super().__init__(*args, **kwargs)

    def clean_type(self):
        """Clean type."""
        return int(self.cleaned_data["type"])

    def clean_name(self):
        """Clean name."""
        return self.cleaned_data["name"] or None

    def clean_isin(self):
        """Clean isin."""
        return self.cleaned_data["isin"] or None

    def clean_wkn(self):
        """Clean wkn."""
        return self.cleaned_data["wkn"] or None

    def clean_symbol(self):
        """Clean symbol."""
        return self.cleaned_data["symbol"] or None

    def save(self, commit=True):
        """Save."""
        print(self.cleaned_data)
        if self.cleaned_data["type"] == 0:
            etf = ETF(
                name=self.cleaned_data["name"],
                isin=self.cleaned_data["isin"],
                wkn=self.cleaned_data["wkn"],
                symbol=self.cleaned_data["symbol"],
                currency=self.cleaned_data["currency"],
                traded=self.cleaned_data["traded"],
            )
            etf.save()
            return etf
        elif self.cleaned_data["type"] == 1:
            fund = Fund(
                name=self.cleaned_data["name"],
                isin=self.cleaned_data["isin"],
                wkn=self.cleaned_data["wkn"],
                symbol=self.cleaned_data["symbol"],
                currency=self.cleaned_data["currency"],
                traded=self.cleaned_data["traded"],
            )
            fund.save()
            return fund
        elif self.cleaned_data["type"] == 2:
            stock = Stock(
                name=self.cleaned_data["name"],
                isin=self.cleaned_data["isin"],
                wkn=self.cleaned_data["wkn"],
                symbol=self.cleaned_data["symbol"],
                currency=self.cleaned_data["currency"],
                traded=self.cleaned_data["traded"],
            )
            stock.save()
            return stock

    class Meta:
        """Meta."""

        model = Tradeable
        fields = ("type", "name", "isin", "wkn", "symbol", "currency", "traded")


class PositionForm(forms.ModelForm):
    """Position model form."""

    tradeable = forms.ChoiceField(
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        self.fields["tradeable"].choices = (
            [(None, "")]
            + [(f"etf:{etf.pk}", etf.name) for etf in ETF.objects.all()]
            + [(f"fund:{fund.pk}", fund.name) for fund in Fund.objects.all()]
            + [(f"stock:{stock.pk}", stock.name) for stock in Stock.objects.all()]
        )
        self.fields["tradeable"].widget.attrs[
            "style"
        ] = "min-width: 113px !important; max-width: 352px !important;"

        if "instance" not in kwargs or kwargs["instance"] is None:
            self.fields["closed"].widget = forms.HiddenInput()

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()

        tradeable = cleaned_data["tradeable"]
        if tradeable.startswith("etf:"):
            tradeable, created = ETF.objects.get_or_create(
                pk=tradeable.replace("etf:", "")
            )
        elif tradeable.startswith("fund:"):
            tradeable, created = Fund.objects.get_or_create(
                pk=tradeable.replace("fund:", "")
            )
        elif tradeable.startswith("stock:"):
            tradeable, created = Stock.objects.get_or_create(
                pk=tradeable.replace("stock:", "")
            )
        cleaned_data["tradeable"] = tradeable

        return cleaned_data

    def save(self, commit=True):
        """Save."""
        instance = super().save(commit=False)
        instance.content_object = self.cleaned_data["tradeable"]
        instance.save()

        return instance

    class Meta:
        """Meta."""

        model = Position
        fields = ("tradeable", "unit", "trailing_stop_atr_factor", "closed")


class PositionFilterForm(forms.Form):
    """Position filter form."""

    closed = forms.ChoiceField(
        choices=[
            (0, _("All positions")),
            (False, _("Opened positions")),
            (True, _("Closed positions")),
        ],
        required=False,
    )
    tradeables = forms.MultipleChoiceField(
        choices=[],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        self.fields["tradeables"].choices = (
            [(f"etf:{etf.pk}", etf.name) for etf in ETF.objects.all()]
            + [(f"fund:{fund.pk}", fund.name) for fund in Fund.objects.all()]
            + [(f"stock:{stock.pk}", stock.name) for stock in Stock.objects.all()]
        )
        self.fields["tradeables"].widget.attrs[
            "style"
        ] = "min-width: 113px !important; max-width: 352px !important;"


class TradeForm(forms.ModelForm):
    """Trade model form."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        self.fields["units"].localize = True
        self.fields["units"].widget = forms.TextInput(attrs={"step": "any"})
        self.fields["unit_price"].localize = True
        self.fields["unit_price"].widget = forms.TextInput(attrs={"step": "any"})
        self.fields["extra"].localize = True
        self.fields["extra"].widget = forms.TextInput(attrs={"step": "any"})
        self.fields["extra"].help_text = _("Applied before exchange rate.")
        self.fields["extra2"].localize = True
        self.fields["extra2"].widget = forms.TextInput(attrs={"step": "any"})
        self.fields["extra2"].help_text = _("Applied after exchange rate.")

        self.fields["date"].help_text = mark_safe(
            '<a id="date_today" href="">%s</a> (%s)'
            % (_("Today"), _("Date format: yyyy-mm-dd"))
        )
        self.fields["date"].localize = True

    def clean_exchange_rate(self):
        """Clean exchange_rate."""
        return self.cleaned_data["exchange_rate"] or None

    class Meta:
        """Meta."""

        model = Trade
        fields = (
            "position",
            "type",
            "date",
            "units",
            "unit_price",
            "extra",
            "unit",
            "exchange_rate",
            "extra2",
        )


class ClosingForm(forms.ModelForm):
    """Closing model form."""

    date_field = forms.CharField(
        initial=CLOSING_FORM_INITIAL_DATE_FIELD,
        help_text=_("Name of the date column"),
        label=_("Date"),
    )
    dateformat = forms.CharField(
        initial=CLOSING_FORM_DATEFORMAT,
        help_text=_("Date format using the 1989 C standard codes."),
        label=_("Date format"),
    )
    price_field = forms.CharField(
        initial=CLOSING_FORM_INITIAL_PRICE_FIELD,
        help_text=_("Name of the price column"),
        label=_("Price"),
    )
    low_field = forms.CharField(
        initial=CLOSING_FORM_INITIAL_LOW_FIELD,
        help_text=_("Name of the low column"),
        label=_("Low"),
    )
    high_field = forms.CharField(
        initial=CLOSING_FORM_INITIAL_HIGH_FIELD,
        help_text=_("Name of the high column"),
        label=_("High"),
    )
    tradeable = forms.ChoiceField(
        choices=[],
    )
    data = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 100, "rows": 18, "style": "width: 100%;"}),
        label=_("Data"),
    )

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

        self.fields["tradeable"].choices = (
            [(None, "")]
            + [(etf.slug, etf.name) for etf in ETF.objects.all()]
            + [(fund.slug, fund.name) for fund in Fund.objects.all()]
            + [(stock.slug, stock.name) for stock in Stock.objects.all()]
        )
        self.fields["tradeable"].widget.attrs[
            "style"
        ] = "min-width: 113px !important; max-width: 352px !important;"

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()

        lines = cleaned_data["data"].split("\n")
        fields = [field.strip() for field in lines[0].split("\t")]
        for i in range(len(fields)):
            if fields[i] == self.cleaned_data["date_field"]:
                fields[i] = "date"
            elif fields[i] == self.cleaned_data["high_field"]:
                fields[i] = "high"
            elif fields[i] == self.cleaned_data["low_field"]:
                fields[i] = "low"
            elif fields[i] == self.cleaned_data["price_field"]:
                fields[i] = "price"

        cleaned_data["data"] = []
        for line in lines[1:]:
            if line.strip():
                cleaned_data["data"].append({})
                for field, value in zip(fields, line.strip().split("\t")):
                    if field == "date":
                        cleaned_data["data"][-1][field] = datetime.strptime(
                            value.strip(),
                            cleaned_data["dateformat"],
                        )
                    elif field in ["price", "high", "low"]:
                        cleaned_data["data"][-1][field] = float(
                            formats.sanitize_separators(value.strip())
                        )

        tradeable = cleaned_data["tradeable"]
        if tradeable.startswith("etf:"):
            tradeable, created = ETF.objects.get_or_create(
                pk=tradeable.replace("etf:", "")
            )
        elif tradeable.startswith("fund:"):
            tradeable, created = Fund.objects.get_or_create(
                pk=tradeable.replace("fund:", "")
            )
        elif tradeable.startswith("stock:"):
            tradeable, created = Stock.objects.get_or_create(
                pk=tradeable.replace("stock:", "")
            )
        cleaned_data["tradeable"] = tradeable

        return cleaned_data

    def save(self, commit: bool = True):
        """Save."""

        content_type = ContentType.objects.get_for_model(self.cleaned_data["tradeable"])

        closings = []
        for i in self.cleaned_data["data"]:
            if "date" in i and "price" in i and "high" in i and "low" in i:
                closings.append(
                    Closing.objects.update_or_create(
                        content_type=content_type,
                        object_id=self.cleaned_data["tradeable"].pk,
                        date=i["date"],
                        defaults={
                            "price": i["price"],
                            "high": i["high"],
                            "low": i["low"],
                        },
                    )[0]
                )
        return closings

    class Meta:
        """Meta."""

        model = Closing
        fields = (
            "tradeable",
            "date_field",
            "dateformat",
            "price_field",
            "low_field",
            "high_field",
            "data",
        )
