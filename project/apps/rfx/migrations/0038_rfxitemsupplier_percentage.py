# Generated by Django 3.0 on 2023-06-16 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfx', '0037_auto_20230217_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfxitemsupplier',
            name='percentage',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
