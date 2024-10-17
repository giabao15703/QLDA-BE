# Generated by Django 3.0 on 2024-08-25 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0059_auto_20240512_1857'),
        ('order', '0003_auto_20240825_0649'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='onsignee',
            field=models.ForeignKey(default=74, on_delete=django.db.models.deletion.CASCADE, related_name='order_onsignee', to='users.Supplier'),
            preserve_default=False,
        ),
    ]
