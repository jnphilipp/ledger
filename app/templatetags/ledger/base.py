from app.templatetags.ledger import register

@register.filter
def decrement(value):
    return int(value) - 1

@register.filter
def increment(value):
    return int(value) + 1

@register.filter
def lookup(d, key):
    return d[key] if key in d else None

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

@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class":css})