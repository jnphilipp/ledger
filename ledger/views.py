# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic


@method_decorator(login_required, name='dispatch')
class AnotherSuccessView(generic.base.TemplateView):
    template_name = 'ledger/another_success.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AnotherSuccessView, self).get_context_data(*args,
                                                                   **kwargs)
        if 'reload' in self.request.GET:
            context['reload'] = bool(self.request.GET.get('reload'))
        else:
            context['reload'] = False
        if 'target_id' in self.request.GET:
            context['target_id'] = self.request.GET.get('target_id')
        if 'value' in self.request.GET:
            context['value'] = self.request.GET.get('value')
        if 'name' in self.request.GET:
            context['name'] = self.request.GET.get('name')

        return context
