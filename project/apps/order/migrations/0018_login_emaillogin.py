# Generated by Django 3.0 on 2024-10-17 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_auto_20241017_0112'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='emailLogin',
            field=models.CharField(default='huit@example.com', max_length=50),
        ),
    ]
