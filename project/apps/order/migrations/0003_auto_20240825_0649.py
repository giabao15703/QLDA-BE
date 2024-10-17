# Generated by Django 3.0 on 2024-08-25 06:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20240825_0410'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='taxCode',
            field=models.CharField(default='FDJQ2', max_length=20),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='OrderDeliveryTimelines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(max_length=255)),
                ('order_date', models.DateTimeField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_delivery_timelines', to='order.Order')),
            ],
            options={
                'db_table': 'order_delivery_timelines',
            },
        ),
    ]