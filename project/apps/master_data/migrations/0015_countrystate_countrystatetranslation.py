# Generated by Django 3.1.5 on 2023-10-02 09:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0014_promotion_apply_scope'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('state_code', models.CharField(max_length=10)),
                ('status', models.BooleanField(default=True, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='state', to='master_data.country')),
            ],
            options={
                'db_table': 'master_data_country_state',
                'unique_together': {('state_code', 'country')},
            },
        ),
        migrations.CreateModel(
            name='CountryStateTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('country_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.countrystate')),
            ],
            options={
                'db_table': 'master_data_country_state_translation',
                'unique_together': {('language_code', 'country_state')},
            },
        ),
    ]
