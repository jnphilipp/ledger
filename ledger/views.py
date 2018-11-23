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
            context['reload'] = bool(self.request.GET.get('reload')[0])
        else:
            context['reload'] = False
        return context
