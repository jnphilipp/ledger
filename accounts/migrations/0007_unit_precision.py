# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_account_ledgers'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='precision',
            field=models.PositiveIntegerField(default=2),
        ),
    ]
