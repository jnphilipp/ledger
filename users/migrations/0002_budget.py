# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 07:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_tag'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('consumption_tags', models.ManyToManyField(blank=True, related_name='consumption_tags', to='categories.Tag', verbose_name='Consumption tags')),
                ('income_tags', models.ManyToManyField(blank=True, related_name='income_tags', to='categories.Tag', verbose_name='Income tags')),
                ('insurance_tags', models.ManyToManyField(blank=True, related_name='insurance_tags', to='categories.Tag', verbose_name='Insurance tags')),
                ('savings_tags', models.ManyToManyField(blank=True, related_name='savings_tags', to='categories.Tag', verbose_name='Savings tags')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Budget',
                'ordering': ('user',),
                'verbose_name_plural': 'Budgets',
            },
        ),
    ]
