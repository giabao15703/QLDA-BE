# Generated by Django 3.0 on 2024-12-06 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0077_auto_20241206_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppermission',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Trưởng khoa'), (2, 'Giáo vụ'), (3, 'Giảng viên'), (4, 'Trưởng bộ môn')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Trưởng khoa'), (2, 'Giáo vụ'), (3, 'Giảng viên'), (4, 'Trưởng bộ môn')], null=True),
        ),
    ]
