# Generated by Django 3.0 on 2021-08-17 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfx', '0021_auto_20210811_0743'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rfx',
            old_name='delivery_from',
            new_name='from_date',
        ),
        migrations.RenameField(
            model_name='rfx',
            old_name='delivery_to',
            new_name='to_date',
        ),
        migrations.RemoveField(
            model_name='rfx',
            name='terms_and_conditions',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='commercial_terms',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='delivery_address_rjected_reason',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='delivery_term_rjected_reason',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='is_delivery_address_accepted',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='is_delivery_term_accepted',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='is_other_requirements_accepted',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='is_payment_term_accepted',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='is_terms_conditions_accepted',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='other_requirements_rjected_reason',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='payment_term_rjected_reason',
        ),
        migrations.RemoveField(
            model_name='rfxsupplier',
            name='terms_conditions_rjected_reason',
        ),
        migrations.AddField(
            model_name='rfxitem',
            name='delivery_from',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rfxitem',
            name='delivery_to',
            field=models.DateField(blank=True, null=True),
        ),
    ]
