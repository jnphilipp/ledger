# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('serial_number', models.IntegerField()),
                ('day', models.DateField()),
                ('amount', models.FloatField(default=0)),
                ('additional', accounts.models.TextFieldSingleLine(blank=True, null=True)),
                ('account', models.ForeignKey(to='accounts.Account')),
                ('category', models.ForeignKey(to='accounts.Category')),
                ('tags', models.ManyToManyField(related_name='entries', blank=True, to='accounts.Tag')),
            ],
            options={
                'verbose_name_plural': 'Entries',
                'ordering': ('account', 'serial_number'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('account', 'serial_number')]),
        ),
    ]
