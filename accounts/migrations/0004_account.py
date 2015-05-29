# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', accounts.models.TextFieldSingleLine()),
                ('slug', models.SlugField(unique=True)),
                ('balance', models.FloatField(default=0)),
                ('category', models.ForeignKey(to='accounts.Category', null=True)),
                ('unit', models.ForeignKey(to='accounts.Unit')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
    ]
