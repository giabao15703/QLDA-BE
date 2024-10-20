# Generated by Django 3.0 on 2020-12-30 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0002_countrytranslation'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitofMeasureTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('unit_of_measure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.UnitofMeasure')),
            ],
            options={
                'db_table': 'master_data_unit_of_measure_translation',
                'unique_together': {('language_code', 'unit_of_measure')},
            },
        ),
        migrations.CreateModel(
            name='TechnicalWeightingTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('technical_weighting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.TechnicalWeighting')),
            ],
            options={
                'db_table': 'master_data_technical_weighting_translation',
                'unique_together': {('language_code', 'technical_weighting')},
            },
        ),
        migrations.CreateModel(
            name='SupplierListTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('supplier_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.SupplierList')),
            ],
            options={
                'db_table': 'master_data_supplier_list_translation',
                'unique_together': {('language_code', 'supplier_list')},
            },
        ),
        migrations.CreateModel(
            name='SubClusterCodeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('sub_cluster_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.SubClusterCode')),
            ],
            options={
                'db_table': 'master_data_sub_cluster_code_translation',
                'unique_together': {('language_code', 'sub_cluster_code')},
            },
        ),
        migrations.CreateModel(
            name='SponsorTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('sponsor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Sponsor')),
            ],
            options={
                'db_table': 'master_data_sponsor_translation',
                'unique_together': {('language_code', 'sponsor')},
            },
        ),
        migrations.CreateModel(
            name='ReasonTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('reason', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Reason')),
            ],
            options={
                'db_table': 'master_data_reason_translation',
                'unique_together': {('language_code', 'reason')},
            },
        ),
        migrations.CreateModel(
            name='PromotionTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=2048)),
                ('promotion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Promotion')),
            ],
            options={
                'db_table': 'master_data_promotion_translation',
                'unique_together': {('language_code', 'promotion')},
            },
        ),
        migrations.CreateModel(
            name='PositionTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Position')),
            ],
            options={
                'db_table': 'master_data_position_translation',
                'unique_together': {('language_code', 'position')},
            },
        ),
        migrations.CreateModel(
            name='PaymentTermTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('payment_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.PaymentTerm')),
            ],
            options={
                'db_table': 'master_data_payment_term_translation',
                'unique_together': {('language_code', 'payment_term')},
            },
        ),
        migrations.CreateModel(
            name='NumberofEmployeeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('number_of_employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.NumberofEmployee')),
            ],
            options={
                'db_table': 'master_data_number_of_employee_translation',
                'unique_together': {('language_code', 'number_of_employee')},
            },
        ),
        migrations.CreateModel(
            name='LevelTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Level')),
            ],
            options={
                'db_table': 'master_data_level_translation',
                'unique_together': {('language_code', 'level')},
            },
        ),
        migrations.CreateModel(
            name='LanguageTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Language')),
            ],
            options={
                'db_table': 'master_data_language_translation',
                'unique_together': {('language_code', 'language')},
            },
        ),
        migrations.CreateModel(
            name='IndustryTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('industry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Industry')),
            ],
            options={
                'db_table': 'master_data_industry_translation',
                'unique_together': {('language_code', 'industry')},
            },
        ),
        migrations.CreateModel(
            name='IndustrySubSectorsTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('industry_sub_sectors', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.IndustrySubSectors')),
            ],
            options={
                'db_table': 'master_data_industry_sub_sectors_translation',
                'unique_together': {('language_code', 'industry_sub_sectors')},
            },
        ),
        migrations.CreateModel(
            name='IndustrySectorsTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('industry_sectors', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.IndustrySectors')),
            ],
            options={
                'db_table': 'master_data_industry_sectors_translation',
                'unique_together': {('language_code', 'industry_sectors')},
            },
        ),
        migrations.CreateModel(
            name='IndustryClusterTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('industry_cluster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.IndustryCluster')),
            ],
            options={
                'db_table': 'master_data_industry_cluster_translation',
                'unique_together': {('language_code', 'industry_cluster')},
            },
        ),
        migrations.CreateModel(
            name='GenderTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Gender')),
            ],
            options={
                'db_table': 'master_data_gender_translation',
                'unique_together': {('language_code', 'gender')},
            },
        ),
        migrations.CreateModel(
            name='FamilyCodeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('family_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.FamilyCode')),
            ],
            options={
                'db_table': 'master_data_family_code_translation',
                'unique_together': {('language_code', 'family_code')},
            },
        ),
        migrations.CreateModel(
            name='EmailTemplatesTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('email_templates', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.EmailTemplates')),
            ],
            options={
                'db_table': 'master_data_email_templates_translation',
                'unique_together': {('language_code', 'email_templates')},
            },
        ),
        migrations.CreateModel(
            name='DeliveryTermTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('delivery_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.DeliveryTerm')),
            ],
            options={
                'db_table': 'master_data_delivery_term_translation',
                'unique_together': {('language_code', 'delivery_term')},
            },
        ),
        migrations.CreateModel(
            name='CurrencyTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Currency')),
            ],
            options={
                'db_table': 'master_data_currency_translation',
                'unique_together': {('language_code', 'currency')},
            },
        ),
        migrations.CreateModel(
            name='ContractTypeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('contract_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.ContractType')),
            ],
            options={
                'db_table': 'master_data_contract_type_translation',
                'unique_together': {('language_code', 'contract_type')},
            },
        ),
        migrations.CreateModel(
            name='ClusterCodeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('cluster_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.ClusterCode')),
            ],
            options={
                'db_table': 'master_data_cluster_code_translation',
                'unique_together': {('language_code', 'cluster_code')},
            },
        ),
        migrations.CreateModel(
            name='ClientFocusTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('client_focus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.ClientFocus')),
            ],
            options={
                'db_table': 'master_data_client_focus_translation',
                'unique_together': {('language_code', 'client_focus')},
            },
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.Category')),
            ],
            options={
                'db_table': 'master_data_category_translation',
                'unique_together': {('language_code', 'category')},
            },
        ),
        migrations.CreateModel(
            name='AuctionTypeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=256)),
                ('auction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='master_data.AuctionType')),
            ],
            options={
                'db_table': 'master_data_auction_type_translation',
                'unique_together': {('language_code', 'auction_type')},
            },
        ),
    ]
