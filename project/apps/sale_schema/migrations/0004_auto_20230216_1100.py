# Generated by Django 3.0 on 2023-02-16 11:00

import apps.sale_schema.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale_schema', '0003_profilefeaturesbuyer_rfx_auto_nego'),
    ]

    operations = [
        migrations.AddField(
            model_name='ourpartner',
            name='link',
            field=models.CharField(blank=True, max_length=2084, null=True),
        ),
        migrations.AddField(
            model_name='ourpartner',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=apps.sale_schema.models.our_partner_directory_path),
        ),
    ]
