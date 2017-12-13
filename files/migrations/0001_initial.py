# Generated by Django 2.0 on 2017-12-11 18:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import files.models
import ledger.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('slug', models.SlugField(max_length=1024, unique=True, verbose_name='Slug')),
                ('name', ledger.fields.SingleLineTextField(verbose_name='Name')),
                ('file', models.FileField(max_length=4096, upload_to=files.models.get_file_path, verbose_name='File')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
                'ordering': ('name',),
            },
        ),
    ]
