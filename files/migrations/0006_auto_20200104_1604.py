# Generated by Django 2.2.8 on 2020-01-04 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0005_migrate_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
        migrations.AlterField(
            model_name='statement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='statement',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
    ]
