# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

def validate_account_name(value):
    if value in ['add', 'entries']:
        raise ValidationError(
            _('"%(value)s" is not a valid account name'),
            code='invalid',
            params={'value': value}
        )

