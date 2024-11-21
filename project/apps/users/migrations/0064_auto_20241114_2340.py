# Generated by Django 3.0 on 2024-11-14 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0063_remove_supplierproduct_certification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='picture',
        ),
        migrations.AddField(
            model_name='admin',
            name='chuyen_nganh',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='admin',
            name='role',
            field=models.IntegerField(choices=[(1, 'Trưởng khoa'), (2, 'Giáo vụ'), (3, 'Giảng viên')], default=3),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(1, 'master'), (2, 'a1'), (3, 'a2'), (4, 'a3')], null=True),
        ),
    ]