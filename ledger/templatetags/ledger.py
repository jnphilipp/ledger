# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.template import Library


register = Library()


@register.filter
def get_item(d, key):
    if type(d) == dict:
        return d[key] if key in d else None
    else:
        return d[key] if key < len(d) else None


@register.filter
def startswith(value, start):
    return value.startswith(start)


@register.filter
def endswith(value, start):
    return value.endswith(start)


@register.filter
def previous(value, arg):
    try:
        return value[int(arg) - 1] if int(arg) - 1 != -1 else None
    except IndexError:
        return None


@register.filter
def next(value, arg):
    try:
        return value[int(arg) + 1]
    except IndexError:
        return None


@register.filter
def mod(num, val):
    return num % val


@register.filter
def content_type_pk(model):
    return ContentType.objects.get_for_model(model).pk
