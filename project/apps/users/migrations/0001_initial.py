# Generated by Django 2.2.5 on 2020-12-04 03:15

import apps.users.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sale_schema', '__first__'),
        ('master_data', '__first__'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('user_type', models.PositiveSmallIntegerField(choices=[(1, 'admin'), (2, 'buyer'), (3, 'supplier')])),
                ('email', models.EmailField(max_length=254)),
                ('activate_token', models.CharField(max_length=40)),
                ('activate_time', models.DateTimeField(null=True)),
                ('first_name', models.CharField(blank=True, max_length=32, null=True)),
                ('last_name', models.CharField(blank=True, max_length=32, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'active'), (2, 'inactive'), (3, 'deactive')], default=1, null=True)),
                ('short_name', models.CharField(blank=True, max_length=32)),
                ('full_name', models.CharField(blank=True, max_length=32, null=True)),
                ('local_time', models.CharField(default='Asia/Ho_Chi_Minh', max_length=32)),
                ('company_position', models.PositiveSmallIntegerField(choices=[(1, 'owner'), (2, 'staff')], default=1)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_short_name', models.CharField(blank=True, max_length=32, null=True)),
                ('company_long_name', models.CharField(blank=True, max_length=96, null=True)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to=apps.users.models.company_logo_directory_path)),
                ('company_tax', models.CharField(max_length=32)),
                ('company_address', models.CharField(max_length=256)),
                ('company_city', models.CharField(max_length=32)),
                ('company_website', models.CharField(max_length=32)),
                ('company_email', models.CharField(blank=True, max_length=32, null=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=apps.users.models.picture_directory_path)),
                ('phone', models.CharField(max_length=32)),
                ('valid_from', models.DateTimeField(auto_now_add=True)),
                ('valid_to', models.DateTimeField(default=apps.users.models.one_year)),
                ('send_mail_30_day', models.DateTimeField(blank=True, null=True)),
                ('send_mail_15_day', models.DateTimeField(blank=True, null=True)),
                ('send_mail_7_day', models.DateTimeField(blank=True, null=True)),
                ('send_mail_expire', models.DateTimeField(blank=True, null=True)),
                ('company_country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Country')),
                ('company_number_of_employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.NumberofEmployee')),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Currency')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Gender')),
                ('language', models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Language')),
                ('level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Level')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Position')),
                ('profile_features', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.ProfileFeaturesBuyer')),
                ('promotion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Promotion')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='buyer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_buyer',
            },
        ),
        migrations.CreateModel(
            name='BuyerSubAccounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=32)),
                ('picture', models.ImageField(null=True, upload_to=apps.users.models.picture_directory_path)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer', to='users.Buyer')),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Currency')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Gender')),
                ('language', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Language')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Position')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_sub_accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_buyer_sub_accounts',
            },
        ),
        migrations.CreateModel(
            name='GroupPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'master'), (2, 'a1'), (3, 'a2'), (4, 'a3')])),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
            options={
                'db_table': 'users_groups_permission',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_short_name', models.CharField(blank=True, max_length=32, null=True)),
                ('company_long_name', models.CharField(blank=True, max_length=96, null=True)),
                ('company_tax', models.CharField(max_length=32)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to=apps.users.models.company_logo_directory_path)),
                ('company_address', models.CharField(max_length=256)),
                ('company_city', models.CharField(max_length=32)),
                ('company_ceo_owner_name', models.CharField(blank=True, max_length=32, null=True)),
                ('company_ceo_owner_email', models.CharField(blank=True, max_length=32, null=True)),
                ('company_website', models.CharField(blank=True, max_length=32, null=True)),
                ('company_credential_profile', models.FileField(blank=True, null=True, upload_to=apps.users.models.company_credential_profile_directory_path)),
                ('company_tag_line', models.CharField(blank=True, max_length=350, null=True)),
                ('company_description', models.CharField(blank=True, max_length=350, null=True)),
                ('company_established_since', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2020)])),
                ('company_anniversary_date', models.DateTimeField(blank=True, null=True)),
                ('phone', models.CharField(max_length=32)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=apps.users.models.picture_directory_path)),
                ('bank_name', models.CharField(blank=True, max_length=32, null=True)),
                ('bank_code', models.CharField(blank=True, max_length=32, null=True)),
                ('bank_address', models.CharField(blank=True, max_length=32, null=True)),
                ('beneficiary_name', models.CharField(blank=True, max_length=32, null=True)),
                ('switch_bic_code', models.CharField(blank=True, max_length=32, null=True)),
                ('bank_account_number', models.CharField(blank=True, max_length=32, null=True)),
                ('international_bank', models.CharField(blank=True, max_length=32, null=True)),
                ('supplier_form_registration', models.FileField(blank=True, null=True, upload_to=apps.users.models.supplier_form_registration_directory_path)),
                ('bank_certification', models.FileField(blank=True, null=True, upload_to=apps.users.models.bank_certification_directory_path)),
                ('quality_certification', models.FileField(blank=True, null=True, upload_to=apps.users.models.quality_certification_directory_path)),
                ('business_license', models.FileField(blank=True, null=True, upload_to=apps.users.models.business_license_directory_path)),
                ('tax_certification', models.FileField(blank=True, null=True, upload_to=apps.users.models.tax_certification_directory_path)),
                ('others', models.FileField(blank=True, null=True, upload_to=apps.users.models.orthers_directory_path)),
                ('valid_from', models.DateTimeField(auto_now_add=True)),
                ('valid_to', models.DateTimeField(default=apps.users.models.one_year)),
                ('send_mail_30_day', models.DateTimeField(blank=True, null=True)),
                ('send_mail_15_day', models.DateTimeField(blank=True, null=True)),
                ('send_mail_7_day', models.DateTimeField(blank=True, null=True)),
                ('send_mail_expire', models.DateTimeField(blank=True, null=True)),
                ('bank_currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_currency', to='master_data.Currency')),
                ('company_country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Country')),
                ('company_number_of_employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.NumberofEmployee')),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='currency', to='master_data.Currency')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Gender')),
                ('language', models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Language')),
                ('level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Level')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Position')),
                ('profile_features', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.ProfileFeaturesSupplier')),
                ('promotion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Promotion')),
                ('sicp_registration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.SICPRegistration')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='supplier', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_supplier',
            },
        ),
        migrations.CreateModel(
            name='UsersPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateTimeField(null=True)),
                ('valid_to', models.DateTimeField(null=True)),
                ('status', models.IntegerField(choices=[(1, 'active'), (2, 'inactive'), (3, 'cancelled'), (4, 'pending')])),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.GroupPermission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_user_permission',
            },
        ),
        migrations.CreateModel(
            name='UserSubstitutionPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('status', models.IntegerField(choices=[(1, 'active'), (2, 'inactive'), (3, 'cancelled'), (4, 'pending')])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.UsersPermission')),
            ],
            options={
                'db_table': 'users_substitution_permission',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'users_token',
            },
        ),
        migrations.CreateModel(
            name='SupplierTaxCertification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_certification', models.FileField(null=True, upload_to=apps.users.models.tax_certifications_directory_path)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_tax_certification', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_tax_certification',
            },
        ),
        migrations.CreateModel(
            name='SupplierQualityCertification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quality_certification', models.FileField(null=True, upload_to=apps.users.models.quality_certifications_directory_path)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_quality_certification', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_quality_certification',
            },
        ),
        migrations.CreateModel(
            name='SupplierPortfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=100)),
                ('project_name', models.CharField(max_length=100)),
                ('value', models.FloatField()),
                ('project_description', models.CharField(max_length=2048)),
                ('image', models.ImageField(null=True, upload_to=apps.users.models.portfolio_image_directory_path)),
                ('user_supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_portfolio', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_portfolio',
            },
        ),
        migrations.CreateModel(
            name='SupplierOthers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other', models.FileField(blank=True, null=True, upload_to=apps.users.models.others_directory_path)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_other', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_others',
            },
        ),
        migrations.CreateModel(
            name='SupplierIndustry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField()),
                ('industry_sub_sectors', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.IndustrySubSectors')),
                ('user_supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_industry',
            },
        ),
        migrations.CreateModel(
            name='SupplierFormRegistrations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_registration', models.FileField(null=True, upload_to=apps.users.models.supplier_form_registrations_directory_path)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_form_registrations', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_form_registration',
            },
        ),
        migrations.CreateModel(
            name='SupplierFlashSale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku_number', models.CharField(max_length=32, unique=True)),
                ('description', models.TextField(default='', max_length=2048)),
                ('picture', models.ImageField(null=True, upload_to=apps.users.models.flash_sale_directory_path)),
                ('initial_price', models.FloatField()),
                ('percentage', models.FloatField()),
                ('user_supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_flash_sale',
            },
        ),
        migrations.CreateModel(
            name='SupplierCompanyCredential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_credential_profile', models.FileField(null=True, upload_to=apps.users.models.company_credential_profiles_directory_path)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_company_credential', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_company_credential',
            },
        ),
        migrations.CreateModel(
            name='SupplierClientFocus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField()),
                ('client_focus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.ClientFocus')),
                ('user_supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_client_focus',
            },
        ),
        migrations.CreateModel(
            name='SupplierCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField()),
                ('minimum_of_value', models.FloatField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Category')),
                ('user_supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_category',
            },
        ),
        migrations.CreateModel(
            name='SupplierBusinessLicense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_license', models.FileField(null=True, upload_to=apps.users.models.business_licenses_directory_path)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_business_license', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_business_license',
            },
        ),
        migrations.CreateModel(
            name='SupplierBankCertification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_certification', models.FileField(null=True, upload_to=apps.users.models.bank_certifications_directory_path)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_bank_certification', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_bank_certification',
            },
        ),
        migrations.CreateModel(
            name='SupplierActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_date', models.DateTimeField(auto_now_add=True)),
                ('reason_manual', models.CharField(max_length=256, null=True)),
                ('changed_state', models.PositiveSmallIntegerField(choices=[(1, 'active'), (2, 'inactive'), (3, 'deactive')])),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_activity', to='users.Supplier')),
            ],
            options={
                'db_table': 'users_supplier_activity',
            },
        ),
        migrations.CreateModel(
            name='ForgotPasswordToken',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_forgot_password_token', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'users_forgot_password_token',
            },
        ),
        migrations.CreateModel(
            name='BuyerSubAccountsActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_date', models.DateTimeField(auto_now_add=True)),
                ('reason_manual', models.CharField(max_length=256, null=True)),
                ('changed_state', models.PositiveSmallIntegerField(choices=[(1, 'active'), (2, 'inactive'), (3, 'deactive')])),
                ('buyer_sub_accounts', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_sub_accounts_activity', to='users.BuyerSubAccounts')),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_buyer_sub_accounts_activity',
            },
        ),
        migrations.CreateModel(
            name='BuyerIndustry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_industry', to='master_data.IndustrySubSectors')),
                ('user_buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_industry', to='users.Buyer')),
            ],
        ),
        migrations.CreateModel(
            name='BuyerActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_date', models.DateTimeField(auto_now_add=True)),
                ('reason_manual', models.CharField(max_length=256, null=True)),
                ('changed_state', models.PositiveSmallIntegerField(choices=[(1, 'active'), (2, 'inactive'), (3, 'deactive')])),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_activity', to='users.Buyer')),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_buyer_activity',
            },
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('long_name', models.CharField(max_length=96)),
                ('picture', models.ImageField(null=True, upload_to=apps.users.models.picture_directory_path)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_admin',
            },
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(fields=('user_type', 'email'), name='user_type_email_unique'),
        ),
    ]
