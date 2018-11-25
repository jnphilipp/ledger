# -*- coding: utf-8 -*-

from accounts.models import Account, Entry
from categories.models import Category, Tag
from django.db.models import Q
from django.template import Library


register = Library()


@register.filter
def accounts(obj, user):
    if isinstance(obj, Category):
        return Account.objects.filter(Q(ledger__user=user) & (Q(category=obj)
                                      | Q(entries__category=obj))).distinct()
    elif isinstance(obj, Tag):
        return Account.objects.filter(Q(ledger__user=user) &
                                      Q(entries__tags=obj)).distinct()
    else:
        return None


@register.filter
def entry_count(obj, user):
    if isinstance(obj, Category):
        return Entry.objects.filter(Q(account__ledger__user=user) &
                                    Q(category=obj)).count()
    elif isinstance(obj, Tag):
        return Entry.objects.filter(Q(account__ledger__user=user) &
                                    Q(tags=obj)).count()
    else:
        return None
