# Generated by Django 3.0 on 2024-08-27 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_auto_20240825_0848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpaymentdetails',
            name='payment_method',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Wallet'), (2, 'BankTransfer'), (3, 'OnePay')]),
        ),
    ]
