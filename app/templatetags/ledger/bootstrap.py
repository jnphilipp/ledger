# -*- coding: utf-8 -*-

from app.templatetags.ledger import register

@register.inclusion_tag('bootstrap/messages.html', takes_context=True)
def bootstrap_messages(context):
    return {'messages': context['messages']}

@register.inclusion_tag('bootstrap/pagination.html', takes_context=True)
def pagination(context, paginator, page, title=None, *args, **kwargs):
    context['prange'] = paginator.page_range[max(int(page.number) - 4, 0):min(int(page.number) + 3, paginator.num_pages)]
    context['page'] = page
    context['title'] = title
    context['kwargs'] = kwargs
    return context
