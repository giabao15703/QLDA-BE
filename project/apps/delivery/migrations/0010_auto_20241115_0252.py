# Generated by Django 3.0 on 2024-11-14 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0009_remove_kehoachdoan_admin'),
    ]

    operations = [
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
