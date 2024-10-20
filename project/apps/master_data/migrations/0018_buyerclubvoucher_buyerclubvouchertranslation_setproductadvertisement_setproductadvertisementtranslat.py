# Generated by Django 3.0 on 2024-10-03 18:50

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0017_voucher_vouchertranslation'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyerClubVoucher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_code', models.CharField(max_length=16, unique=True)),
                ('description', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=True)),
                ('standard', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('gold', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('platinum', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('diamond', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('label', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'db_table': 'master_data_buyer_club_voucher',
            },
        ),
        migrations.CreateModel(
            name='SetProductAdvertisement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(   max_length=255)),
                ('status', models.BooleanField(default=True)),
                ('duration', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(365)])),
                ('serviceFee', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(365)])),
            ],
            options={
                'db_table': 'master_data_set_product_advertisement',
            },
        ),
        migrations.CreateModel(
            name='WarrantyTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warranty_code', models.CharField(max_length=16, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'master_data_warranty_term',
            },
        ),
        migrations.CreateModel(
            name='WarrantyTermTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('warranty_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.WarrantyTerm')),
            ],
            options={
                'db_table': 'master_data_warranty_term_translation',
                'unique_together': {('language_code', 'warranty_term')},
            },
        ),
        migrations.CreateModel(
            name='SetProductAdvertisementTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=256)),
                ('set_product_advertisement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.SetProductAdvertisement')),
            ],
            options={
                'db_table': 'master_data_set_product_advertisement_translation',
                'unique_together': {('language_code', 'set_product_advertisement')},
            },
        ),
        migrations.CreateModel(
            name='BuyerClubVoucherTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=256)),
                ('buyer_club_voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.BuyerClubVoucher')),
            ],
            options={
                'db_table': 'master_data_buyer_club_voucher_translation',
                'unique_together': {('language_code', 'buyer_club_voucher')},
            },
        ),
    ]
