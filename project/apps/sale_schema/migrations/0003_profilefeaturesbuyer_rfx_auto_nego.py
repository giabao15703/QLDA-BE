# Generated by Django 3.0 on 2021-09-07 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale_schema', '0002_ourpartner'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilefeaturesbuyer',
            name='rfx_auto_nego',
            field=models.BooleanField(default=False),
        ),
    ]
