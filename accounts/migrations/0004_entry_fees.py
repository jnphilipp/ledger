# Generated by Django 2.2.5 on 2019-09-18 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_entry'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='fees',
            field=models.FloatField(default=0, verbose_name='Fees'),
        ),
    ]
