# Generated by Django 3.0 on 2024-11-20 23:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0010_auto_20241121_0247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detai',
            name='idnhom',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='groupqlda',
            name='de_tai',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='de_tai', to='delivery.DeTai'),
        ),
    ]
