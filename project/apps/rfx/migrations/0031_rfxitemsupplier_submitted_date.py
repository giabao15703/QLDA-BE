# Generated by Django 3.0 on 2021-09-09 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfx', '0030_rfxsupplier_is_best_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfxitemsupplier',
            name='submitted_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
