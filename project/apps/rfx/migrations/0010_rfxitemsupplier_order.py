# Generated by Django 3.0 on 2021-07-01 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfx', '0009_rfxaward'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfxitemsupplier',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
