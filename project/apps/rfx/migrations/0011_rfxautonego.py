# Generated by Django 3.0 on 2021-07-01 07:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rfx', '0010_rfxitemsupplier_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='RFXAutoNego',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_percentage', models.IntegerField()),
                ('max_percentage', models.IntegerField()),
                ('unit_price', models.FloatField()),
                ('total_amount', models.FloatField()),
                ('rfx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auto_rfxs', to='rfx.RFX')),
                ('rfx_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auto_items', to='rfx.RFXItem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auto_suppliers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'rfx_auto_nego',
            },
        ),
    ]
