# Generated by Django 3.0 on 2023-06-02 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0043_userdiamondsponsor_reach_number_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierproduct',
            name='product_name',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
