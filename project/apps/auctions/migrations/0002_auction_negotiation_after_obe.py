# Generated by Django 3.0 on 2020-12-09 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='negotiation_after_obe',
            field=models.PositiveSmallIntegerField(choices=[(1, 'With negotiation after OBE'), (2, 'Without negotiation after OBE')], default=1),
        ),
    ]
