# Generated by Django 3.0 on 2021-05-20 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20210520_0214'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplierflashsale',
            name='link_path',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
