# Generated by Django 3.0 on 2021-01-18 03:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0005_emailtemplatestranslation_content'),
        ('users', '0003_auto_20210105_0330'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='master_data.Language'),
        ),
    ]
