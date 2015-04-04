# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_account_ledgers'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='category',
            field=models.OneToOneField(to='accounts.Category', null=True),
            preserve_default=True,
        ),
    ]
