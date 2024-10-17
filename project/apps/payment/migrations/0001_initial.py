# Generated by Django 2.2.5 on 2020-12-04 03:14

import apps.payment.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master_data', '__first__'),
        ('sale_schema', '__first__'),
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_information', models.CharField(max_length=256, null=True)),
                ('order_number', models.CharField(max_length=32, null=True)),
                ('bank_account_number', models.CharField(max_length=32)),
                ('day_of_payment', models.DateTimeField()),
                ('amount', models.FloatField()),
                ('auction_number', models.CharField(max_length=8, null=True)),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank', to='master_data.Bank')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_bank_transfer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payment_bank_transfer',
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=8, null=True, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Payment'), (2, 'Deposit'), (3, 'Topup'), (4, 'Refund')])),
                ('transaction_description', models.CharField(max_length=255, null=True)),
                ('balance', models.FloatField(null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Confirmed'), (2, 'Paid'), (3, 'Refunding Deposit'), (4, 'Request refunding'), (5, 'Refunded'), (6, 'Cancelled'), (7, 'Pending'), (8, 'Refunded Deposit'), (9, 'Charged Deposit'), (10, 'Close')])),
                ('invoice_receipt', models.FileField(null=True, upload_to=apps.payment.models.invoice_receipt_directory_path)),
                ('request_draft_invoice', models.FileField(null=True, upload_to=apps.payment.models.request_draft_invoice_directory_path)),
                ('notes', models.CharField(max_length=255, null=True)),
                ('method_payment', models.PositiveSmallIntegerField(choices=[(1, 'Wallet'), (2, 'BankTransfer'), (3, 'OnePay')], null=True)),
                ('amount', models.FloatField(null=True)),
                ('admin_balance', models.FloatField(default=0, null=True)),
                ('is_parent', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'payment_history',
            },
        ),
        migrations.CreateModel(
            name='UserPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('one_pay', models.FloatField(default=0)),
                ('bank_transfer', models.FloatField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_payment', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payment_user_payment',
            },
        ),
        migrations.CreateModel(
            name='PaymentAuction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charge_amount', models.FloatField()),
                ('refund_amount', models.FloatField()),
                ('wallet_type', models.IntegerField(null=True)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_auction', to='auctions.Auction')),
                ('history', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_auction', to='payment.History')),
            ],
            options={
                'db_table': 'payment_auction',
            },
        ),
        migrations.CreateModel(
            name='HistoryPending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='payment.History')),
                ('history_pending', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='history_pending', to='payment.History')),
            ],
            options={
                'db_table': 'payment_history_pending',
            },
        ),
        migrations.CreateModel(
            name='HistoryOnePay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, null=True)),
                ('history', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='history_onepay', to='payment.History')),
                ('profile_features_buyer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.ProfileFeaturesBuyer')),
                ('profile_features_supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.ProfileFeaturesSupplier')),
                ('promotion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Promotion')),
                ('sicp_registration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.SICPRegistration')),
            ],
            options={
                'db_table': 'payment_history_one_pay',
            },
        ),
        migrations.AddField(
            model_name='history',
            name='user_payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_history', to='payment.UserPayment'),
        ),
        migrations.CreateModel(
            name='BankTransferRefund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_account_number', models.CharField(max_length=32)),
                ('amount', models.FloatField()),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_transfer_refund', to='master_data.Bank')),
                ('history', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bank_transfer_refund', to='payment.History')),
            ],
            options={
                'db_table': 'payment_bank_transfer_refund',
            },
        ),
        migrations.CreateModel(
            name='BankTransferPaymentOrderAttached',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=apps.payment.models.payment_order_attached_directory_path)),
                ('bank_transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments_order_attached', to='payment.BankTransfer')),
            ],
            options={
                'db_table': 'payment_bank_transfer__order_attached',
            },
        ),
        migrations.CreateModel(
            name='BankTransferHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_pending', models.BooleanField(default=False)),
                ('bank_transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_transfer', to='payment.BankTransfer')),
                ('history', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bank_transfer_history', to='payment.History')),
                ('profile_features_buyer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.ProfileFeaturesBuyer')),
                ('profile_features_supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.ProfileFeaturesSupplier')),
                ('promotion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='master_data.Promotion')),
                ('sicp_registration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sale_schema.SICPRegistration')),
            ],
            options={
                'db_table': 'payment_bank_transfer_history',
            },
        ),
    ]
