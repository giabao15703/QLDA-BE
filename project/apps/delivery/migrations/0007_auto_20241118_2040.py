# Generated by Django 3.0 on 2024-11-18 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0064_auto_20241114_2340'),
        ('delivery', '0006_auto_20241114_2340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kehoachdoan',
            name='user',
        ),
        migrations.AddField(
            model_name='groupqlda',
            name='creator_short_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='groupqlda',
            name='leader_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='led_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='detai',
            name='idgvhuongdan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='huongdan_detai', to='users.Admin'),
        ),
        migrations.AlterField(
            model_name='detai',
            name='idgvphanbien',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phanbien_detai', to='users.Admin'),
        ),
        migrations.AlterField(
            model_name='groupqlda',
            name='de_tai',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgbd_cham_hoi_dong',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgbd_cham_phan_bien',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgbd_dang_ky_de_tai',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgbd_do_an',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgbd_lam_do_an',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgbd_tao_do_an',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgkt_cham_hoi_dong',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgkt_cham_phan_bien',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgkt_dang_ky_de_tai',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgkt_do_an',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgkt_lam_do_an',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='kehoachdoan',
            name='tgkt_tao_do_an',
            field=models.DateTimeField(),
        ),
    ]