# Generated by Django 3.0 on 2024-10-28 11:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('delivery', '0012_auto_20241028_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_groups', to='delivery.GroupQLDA')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'join_group',
                'unique_together': {('user', 'group')},
            },
        ),
    ]
