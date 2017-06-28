# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 07:20
from __future__ import unicode_literals

import accounts.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('units', '0001_initial'),
        ('categories', '0002_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(unique=True)),
                ('name', accounts.models.TextFieldSingleLine(verbose_name='Name')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accounts', to='categories.Category', verbose_name='Category')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='units.Unit', verbose_name='Unit')),
            ],
            options={
                'verbose_name_plural': 'Accounts',
                'verbose_name': 'Account',
                'ordering': ('closed', 'name'),
            },
        ),
    ]
