from django.utils.numberformat import format
from django.utils.safestring import mark_safe
from accounts.templatetags.accounts_tags import register

@register.filter
def floatdot(value, decimal_pos=2):
	if not value:
		return format(0, ",", decimal_pos)
	else:
		return format(round(value, decimal_pos), ",", decimal_pos)
floatdot.is_safe = True

@register.filter
def decrement(value):
	return int(value) - 1

@register.filter
def increment(value):
	return int(value) + 1

@register.filter
def lookup(d, key):
	return d[key]

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

@register.filter(needs_autoescape=True)
def colorfy(amount, currency=None, autoescape=None):
	return mark_safe('<span class="%s">%s %s</span>' % ('green' if amount >= 0 else 'red', floatdot(amount, 2), currency.symbol if currency else ''))

@register.filter(name='addcss')
def addcss(field, css):
	return field.as_widget(attrs={"class":css})