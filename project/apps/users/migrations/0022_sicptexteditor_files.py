# Generated by Django 3.0 on 2021-05-21 06:37

import apps.users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_auto_20210520_0708'),
    ]

    operations = [
        migrations.AddField(
            model_name='sicptexteditor',
            name='files',
            field=models.FileField(blank=True, null=True, upload_to=apps.users.models.sicp_file_path),
        ),
    ]
