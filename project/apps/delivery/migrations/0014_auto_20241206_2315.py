# Generated by Django 3.0 on 2024-12-06 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0013_auto_20241206_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joinrequest',
            name='request_type',
            field=models.CharField(choices=[('joinRequest', 'Join Request'), ('invite', 'Invite')], default='joinRequest', max_length=20),
        ),
    ]
