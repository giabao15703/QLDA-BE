# Generated by Django 3.0 on 2024-11-20 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0007_auto_20241118_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupqlda',
            name='creator_short_name',
        ),
    ]
