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
"""Portfolio Django app models."""

from datetime import date
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from units.models import Unit
from typing import Optional


class Tradeable(models.Model):
    """Abstract Tradeable Model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    name = models.CharField(max_length=1024, unique=True, verbose_name=_("Name"))
    isin = models.CharField(
        max_length=12, unique=True, blank=True, null=True, verbose_name=_("ISIN")
    )
    wkn = models.CharField(
        max_length=6, unique=True, blank=True, null=True, verbose_name=_("WKN")
    )
    symbol = models.CharField(
        max_length=12, unique=True, blank=True, null=True, verbose_name=_("Symbol")
    )
    currency = models.ForeignKey(
        Unit,
        models.SET_NULL,
        related_name="%(class)ss",
        related_query_name="%(app_label)s_%(class)ss",
        blank=True,
        null=True,
        verbose_name=_("Currency"),
    )
    traded = models.BooleanField(default=True, verbose_name=_("Traded"))
    positions = GenericRelation(
        "Position",
        related_query_name="%(app_label)s_%(class)ss",
        verbose_name=_("Tradeable"),
    )
    closings = GenericRelation(
        "Closing",
        related_query_name="%(app_label)s_%(class)ss",
        verbose_name=_("Closing"),
    )

    def save(self, *args, **kwargs):
        """Save."""
        if not self.slug:
            self.slug = slugify(f"{self.name} {self.isin}")
        else:
            orig = self.__class__.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(f"{self.name} {self.isin}")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Name."""
        return f"{self.name} [{self.symbol}]" if self.symbol else self.name

    class Meta:
        """Meta."""

        abstract = True
        ordering = ("name",)
        verbose_name = _("Tradeable")
        verbose_name_plural = _("Tradeables")


class Stock(Tradeable):
    """Stock Model."""

    class Meta(Tradeable.Meta):
        """Meta."""

        verbose_name = _("Stock")
        verbose_name_plural = _("Stocks")


class Fund(Tradeable):
    """Fund Model."""

    class Meta(Tradeable.Meta):
        """Meta."""

        verbose_name = _("Fund")
        verbose_name_plural = _("Funds")


class ETF(Tradeable):
    """ETF Model."""

    class Meta(Tradeable.Meta):
        """Meta."""

        verbose_name = _("ETF")
        verbose_name_plural = _("ETFs")


class Closing(models.Model):
    """Closing Model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    date = models.DateField(verbose_name=_("Date"))
    price = models.FloatField(verbose_name=_("Price"))
    high = models.FloatField(default=0, verbose_name=_("High"))
    low = models.FloatField(default=0, verbose_name=_("Low"))
    change_previous = models.FloatField(default=0, verbose_name=_("Absolute change"))
    change_previous_percent = models.FloatField(
        default=0, verbose_name=_("Relative change")
    )
    content_type = models.ForeignKey(
        ContentType, models.CASCADE, related_name="closings"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def save(self, *args, **kwargs):
        """Save."""
        prev = (
            self.__class__.objects.filter(content_type=self.content_type)
            .filter(object_id=self.object_id)
            .filter(date__lte=self.date)
            .last()
        )
        if prev:
            print(prev.date, self.date)
            self.change_previous = prev.price - self.price
            self.change_previous_percent = self.change_previous / prev.price * 100
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Name."""
        return f"{self.content_type} {self.object_id} [{self.date}]"

    class Meta:
        """Meta."""

        ordering = ("content_type", "object_id", "-date")
        unique_together = ("date", "content_type", "object_id")
        verbose_name = _("Closing")
        verbose_name_plural = _("Closings")


class Position(models.Model):
    """Position Model."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    slug = models.SlugField(max_length=1024, unique=True, verbose_name=_("Slug"))
    content_type = models.ForeignKey(
        ContentType, models.CASCADE, related_name="positions"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    closed = models.BooleanField(default=False, verbose_name=_("Closed"))
    trailing_stop_atr_factor = models.FloatField(
        default=3, verbose_name=_("Trailing-stop ATR factor")
    )
    unit = models.ForeignKey(
        Unit,
        models.CASCADE,
        related_name="positions",
        verbose_name=_("Unit"),
    )

    def start_date(self) -> date:
        """Start date i.e. date of the first trade."""
        return (
            self.trades.aggregate(models.Min("date"))["date__min"]
            if self.trades.exists()
            else timezone.now().date()
        )

    def end_date(self) -> date:
        """End date, i.e., date of the last trade or current date."""
        today = timezone.now().date()
        if not self.trades.exists():
            return today

        last_trade = self.trades.aggregate(models.Max("date"))["date__max"]
        if self.closed:
            return last_trade
        elif self.content_object.closings.count() == 0:
            return today if today > last_trade else last_trade

        last_closing = self.content_object.closings.first().date
        if last_closing > today and last_closing > last_trade:
            return last_closing
        elif last_trade > today and last_trade > last_closing:
            return last_trade
        else:
            return today

    def duration(self) -> int:
        """Position duration in days."""
        return (self.end_date() - self.start_date()).days

    def dividend(self, date=None) -> float:
        """Dividend."""
        trades = self.trades.filter(date__lte=date) if date else self.trades.all()
        return sum(
            [trade.total() for trade in trades.filter(type=Trade.TradeType.DIVIDEND)]
        )

    def invested(self) -> float:
        """Invested amount."""
        if self.closed:
            return 0.0
        buy = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.BUY)]
        )
        sell = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.SELL)]
        )
        return buy - sell

    def units(self, date=None) -> Optional[float]:
        """Units."""
        if self.trades.count() == 0:
            return None

        trades = self.trades.all()
        if date is not None:
            trades = trades.filter(date__lte=date)
        elif date is None and self.closed:
            return 0

        bought = trades.filter(type=Trade.TradeType.BUY).aggregate(
            units=Coalesce(Sum("units"), 0.0)
        )["units"]
        sold = trades.filter(type=Trade.TradeType.SELL).aggregate(
            units=Coalesce(Sum("units"), 0.0)
        )["units"]
        return round(bought - sold, 5)

    def preturn(self) -> Optional[float]:
        """Return."""
        if self.trades.count() == 0:
            return None

        preturn = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.SELL)]
        )

        if self.content_object.closings.count() == 0 and not self.closed:
            preturn += (
                self.units()
                * self.trades.filter(
                    Q(type=Trade.TradeType.BUY) | Q(type=Trade.TradeType.SELL)
                )
                .first()
                .unit_price
            )
        elif not self.closed:
            preturn += self.units() * self.content_object.closings.first().price

        return preturn

    def win_loss(self) -> Optional[float]:
        """Win / loss."""
        if self.trades.count() == 0:
            return None

        bought = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.BUY)]
        )
        sold = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.SELL)]
        )

        pyield = 0.0
        if self.content_object.closings.count() == 0 and not self.closed:
            pyield = (
                (
                    self.units()
                    * self.trades.filter(
                        Q(type=Trade.TradeType.BUY) | Q(type=Trade.TradeType.SELL)
                    )
                    .first()
                    .unit_price
                )
                + sold
                - bought
            )
        elif not self.closed:
            pyield = (
                (self.units() * self.content_object.closings.first().price)
                + sold
                - bought
            )
        else:
            pyield = sold - bought

        return pyield

    def annual_return(self) -> Optional[float]:
        """Annual return."""
        if self.trades.filter(type=Trade.TradeType.BUY).count() == 0:
            return None

        costs = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.BUY)]
        )
        bought = self.trades.filter(type=Trade.TradeType.BUY).aggregate(
            units=Coalesce(Sum("units"), 0.0)
        )["units"]
        gain = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.SELL)]
        )
        sold = self.trades.filter(type=Trade.TradeType.SELL).aggregate(
            units=Coalesce(Sum("units"), 0.0)
        )["units"]

        if self.content_object.closings.count() == 0 and not self.closed:
            gain += self.trades.filter(
                Q(type=Trade.TradeType.BUY) | Q(type=Trade.TradeType.SELL)
            ).first().unit_price * (bought - sold)
        elif not self.closed:
            gain += self.content_object.closings.first().price * (bought - sold)

        time = self.duration()
        return (pow(gain / costs, 365 / time) - 1) * 100 if time > 0 else 0.0

    def pyield(self) -> Optional[float]:
        """Yield."""
        if self.trades.filter(type=Trade.TradeType.BUY).count() == 0:
            return None

        if self.content_object.closings.count() == 0:
            cur_price = (
                self.trades.filter(
                    Q(type=Trade.TradeType.BUY) | Q(type=Trade.TradeType.SELL)
                )
                .first()
                .unit_price
            )
        elif not self.closed:
            cur_price = self.content_object.closings.first().price

        sum_buy = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.BUY)]
        )

        sum_sell = sum(
            [trade.total() for trade in self.trades.filter(type=Trade.TradeType.SELL)]
        )
        if not self.closed:
            sum_sell += cur_price * self.units()

        return (sum_sell * 100 / sum_buy) - 100

    def renumber_trades(self):
        """Renumber trades."""
        for i, trade in enumerate(self.trades.order_by("serial_number")):
            trade.serial_number = i + 1
            trade.save()

    def save(self, *args, **kwargs):
        """Save."""
        self.slug = slugify(
            f"{self.content_object.name}-{self.start_date().strftime('%Y%m%d')}"
        )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Name."""
        if self.closed:
            return (
                f"{self.content_object.name} "
                + f"[{self.start_date().strftime('%Y-%m-%d')}, {_('closed')}]"
            )
        else:
            return (
                f"{self.content_object.name} [{self.start_date().strftime('%Y-%m-%d')}]"
            )

    class Meta:
        """Meta."""

        ordering = ("closed", "slug")
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")


class Trade(models.Model):
    """Trade Model."""

    class TradeType(models.IntegerChoices):
        """Trade type interger choices."""

        BUY = 0, _("Buy")
        SELL = 1, _("Sell")
        DIVIDEND = 2, _("Dividend")

        __empty__ = _("(Unknown)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    serial_number = models.IntegerField(verbose_name=_("Serial number"))
    date = models.DateField(verbose_name=_("Date"))
    units = models.FloatField(default=0.0, verbose_name=_("Units"))
    unit_price = models.FloatField(default=0.0, verbose_name=_("Unit price"))
    extra = models.FloatField(default=0.0, verbose_name=_("Extra costs"))
    extra2 = models.FloatField(default=0.0, verbose_name=_("Extra costs"))
    exchange_rate = models.FloatField(
        blank=True, null=True, verbose_name=_("Exchange rate")
    )
    type = models.IntegerField(choices=TradeType.choices, verbose_name=_("Type"))
    unit = models.ForeignKey(
        Unit,
        models.CASCADE,
        related_name="trades",
        verbose_name=_("Unit"),
    )
    position = models.ForeignKey(
        Position, models.CASCADE, related_name="trades", verbose_name=_("Position")
    )

    def total(self) -> float:
        """Total."""
        total = 0.0
        if self.type == Trade.TradeType.BUY:
            total = self.unit_price * self.units + self.extra
        elif self.type == Trade.TradeType.SELL or self.type == Trade.TradeType.DIVIDEND:
            total = self.unit_price * self.units - self.extra
        total = round(total, self.unit.precision)
        if self.exchange_rate:
            total = round(total / self.exchange_rate, self.position.unit.precision)
            if self.type == Trade.TradeType.BUY:
                total += self.extra2
            elif (
                self.type == Trade.TradeType.SELL
                or self.type == Trade.TradeType.DIVIDEND
            ):
                total -= self.extra2
        return total

    def save(self, *args, **kwargs):
        """Save."""
        move = False
        old_position = None
        if self.id:
            orig = Trade.objects.get(id=self.id)
            trade = (
                Trade.objects.filter(position=self.position)
                .filter(date__lte=self.date)
                .first()
            )
            next_snr = trade.serial_number + 1 if trade else 1
            if orig.date != self.date and (orig.serial_number + 1) != next_snr:
                move = True
            if orig.position != self.position:
                move = True
                self.serial_number = None
                old_position = orig.position
        if not self.id or move:
            trades = Trade.objects.filter(position=self.position).filter(
                date__lte=self.date
            )
            if trades.exists():
                next_snr = trades.first().serial_number + 1
            else:
                next_snr = 1

            trades = Trade.objects.filter(position=self.position).filter(
                serial_number__gte=next_snr
            )
            for trade in trades:
                trade.serial_number += 1
                trade.save()
            self.serial_number = next_snr
        super().save()
        self.position.save()

        if old_position:
            old_position.renumber_trades()
            old_position.save()

    def __str__(self) -> str:
        """Name."""
        return f"{self.position} #{self.serial_number}"

    class Meta:
        """Meta."""

        ordering = ("position", "-serial_number")
        unique_together = ("position", "serial_number")
        verbose_name = _("Trade")
        verbose_name_plural = _("Trades")
