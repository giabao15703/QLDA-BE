# Generated by Django 3.0 on 2024-10-22 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0022_auto_20241022_0221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupstudent',
            name='giang_vien',
        ),
        migrations.RemoveField(
            model_name='groupstudent',
            name='members',
        ),
        migrations.DeleteModel(
            name='GiangVien',
        ),
        migrations.DeleteModel(
            name='GroupStudent',
        ),
    ]
