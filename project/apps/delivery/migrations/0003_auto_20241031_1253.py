# Generated by Django 3.0 on 2024-10-31 05:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('delivery', '0002_deliveryresponsible_giangvien_groupqlda_transporterlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeTai',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ten_de_tai', models.CharField(max_length=255)),
                ('mo_ta', models.TextField()),
                ('giang_vien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'detai',
            },
        ),
        migrations.CreateModel(
            name='JoinGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='member', max_length=20)),
            ],
            options={
                'db_table': 'join_group',
            },
        ),
        migrations.CreateModel(
            name='JoinRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('leader_user_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'join_request',
            },
        ),
        migrations.DeleteModel(
            name='GiangVien',
        ),
        migrations.AddField(
            model_name='groupqlda',
            name='member_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='joinrequest',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to='delivery.GroupQLDA'),
        ),
        migrations.AddField(
            model_name='joinrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='joingroup',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_groups', to='delivery.GroupQLDA'),
        ),
        migrations.AddField(
            model_name='joingroup',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='joinrequest',
            unique_together={('user', 'group')},
        ),
        migrations.AlterUniqueTogether(
            name='joingroup',
            unique_together={('user', 'group')},
        ),
    ]