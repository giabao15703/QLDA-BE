# Generated by Django 3.0 on 2021-05-27 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_userdiamondsponsorfee'),
        ('payment', '0002_auto_20210527_0811'),
    ]

    operations = [
        migrations.AddField(
            model_name='banktransfer',
            name='diamond_sponsor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.UserDiamondSponsor'),
        ),
    ]
