# Generated by Django 3.0 on 2023-02-24 03:05

import apps.banner.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BannerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_code', models.CharField(max_length=250, unique=True)),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(blank=True, max_length=10000, null=True)),
            ],
            options={
                'db_table': 'banner_banner_group',
            },
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('file', models.FileField(upload_to=apps.banner.models.banner_directory_path)),
                ('file_mobile', models.FileField(blank=True, null=True, upload_to=apps.banner.models.banner_mobile_directory_path)),
                ('link', models.CharField(blank=True, max_length=1000, null=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('description', models.CharField(blank=True, max_length=10000, null=True)),
                ('animation', models.CharField(blank=True, max_length=100, null=True)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='banners', to='banner.BannerGroup')),
            ],
            options={
                'db_table': 'banner_banner',
            },
        ),
    ]
