# Generated by Django 3.0 on 2023-03-01 09:41

import apps.banner.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banner', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=apps.banner.models.banner_directory_path),
        ),
    ]
