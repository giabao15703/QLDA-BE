# Generated by Django 3.0 on 2024-12-08 09:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('delivery', '0016_auto_20241208_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joinrequest',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests_groups', to='delivery.GroupQLDA'),
        ),
        migrations.AlterField(
            model_name='joinrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
