# Generated by Django 3.0 on 2021-06-15 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_userdiamondsponsor_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdiamondsponsor',
            name='order',
        ),
    ]
