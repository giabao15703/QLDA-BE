# Generated by Django 3.0 on 2021-05-18 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_suppliersicp_text_editer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppliersicpfile',
            name='sicp_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'bank_account'), (2, 'certification_management'), (3, 'due_diligence'), (4, 'financial_risk_management'), (5, 'legal_status'), (6, 'document_internal'), (7, 'document_external')]),
        ),
    ]
