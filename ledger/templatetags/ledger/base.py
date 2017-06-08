# -*- coding: utf-8 -*-

from . import register


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
def previous(value, arg):
    try:
        return value[int(arg) - 1] if int(arg) - 1 != -1 else None
    except:
        return None


@register.filter
def next(value, arg):
    try:
        return value[int(arg) + 1]
    except:
        return None
