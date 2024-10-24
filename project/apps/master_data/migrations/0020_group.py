# Generated by Django 3.0 on 2024-10-17 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0019_auto_20241006_2359'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('member', models.IntegerField(default=0)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'group',
            },
        ),
    ]
