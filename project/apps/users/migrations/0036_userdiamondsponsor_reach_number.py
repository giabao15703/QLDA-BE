# Generated by Django 3.0 on 2023-02-27 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_auto_20230227_0636'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdiamondsponsor',
            name='reach_number',
            field=models.IntegerField(default=0),
        ),
    ]
