import os

from apps.auctions.models import Auction
from apps.master_data.models import Bank, Promotion
from apps.sale_schema.models import SICPRegistration, ProfileFeaturesBuyer, ProfileFeaturesSupplier
from apps.users.models import User, UserDiamondSponsor
from django.contrib.auth import get_user_model
from django.db import models
from apps.order.models import (
    Order,
)

User = get_user_model()

PAYMENT_STATUS_CHOICES = (
    (1, 'Confirmed'),
    (2, 'Paid'),
    (3, 'Refunding Deposit'),
    (4, 'Request refunding'),
    (5, 'Refunded'),
    (6, 'Cancelled'),
    (7, 'Pending'),
    (8, 'Refunded Deposit'),
    (9, 'Charged Deposit'),
    (10, 'Close'),
)

TYPE_CHOICES = ((1, 'Payment'), (2, 'Deposit'), (3, 'Topup'), (4, 'Refund'))

METHOD_PAYMENT_CHOICES = ((1, 'Wallet'), (2, 'BankTransfer'), (3, 'OnePay'))

def invoice_receipt_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('invoice_receipt', filename.split('.')[-1]))

def request_draft_invoice_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('request_draft_invoice', filename.split('.')[-1]))

def payment_order_attached_directory_path(instance, filename):
    return os.path.join(str(instance.bank_transfer.user.id), "{}.{}".format('payment_order_attached', filename.split('.')[-1]))

# Create your models here.
class UserPayment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_payment')
    one_pay = models.FloatField(default=0)
    bank_transfer = models.FloatField(default=0)

    class Meta:
        db_table = 'payment_user_payment'

class History(models.Model):
    user_payment = models.ForeignKey(UserPayment, on_delete=models.CASCADE, related_name='user_history')
    order_no = models.CharField(max_length=8, unique=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null=False)
    transaction_description = models.CharField(max_length=255, null=True)
    balance = models.FloatField(null=True)
    status = models.PositiveSmallIntegerField(choices=PAYMENT_STATUS_CHOICES, null=False)
    invoice_receipt = models.FileField(upload_to=invoice_receipt_directory_path, null=True)
    request_draft_invoice = models.FileField(upload_to=request_draft_invoice_directory_path, null=True)
    notes = models.CharField(max_length=255, null=True)
    method_payment = models.PositiveSmallIntegerField(choices=METHOD_PAYMENT_CHOICES, null=True)
    amount = models.FloatField(null=True)
    admin_balance = models.FloatField(null=True, default=0)
    is_parent = models.BooleanField(default=True)

    class Meta:
        db_table = 'payment_history'

class BankTransfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bank_transfer')
    bank_information = models.CharField(max_length=256, null=True)
    order_number = models.CharField(max_length=32, null=True)
    bank_account_number = models.CharField(max_length=32)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='bank')
    day_of_payment = models.DateTimeField()
    amount = models.FloatField()
    auction_number = models.CharField(max_length=8, null=True)
    diamond_sponsor = models.ForeignKey(UserDiamondSponsor, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "payment_bank_transfer"

class BankTransferPaymentOrderAttached(models.Model):
    bank_transfer = models.ForeignKey(BankTransfer, on_delete=models.CASCADE, related_name='payments_order_attached')
    file = models.FileField(upload_to=payment_order_attached_directory_path)

    class Meta:
        db_table = "payment_bank_transfer__order_attached"

class BankTransferHistory(models.Model):
    bank_transfer = models.ForeignKey(BankTransfer, on_delete=models.CASCADE, related_name='bank_transfer')
    history = models.OneToOneField(History, on_delete=models.CASCADE, related_name='bank_transfer_history')
    sicp_registration = models.ForeignKey(SICPRegistration, on_delete=models.CASCADE, null=True)
    profile_features_buyer = models.ForeignKey(ProfileFeaturesBuyer, on_delete=models.CASCADE, null=True)
    profile_features_supplier = models.ForeignKey(ProfileFeaturesSupplier, on_delete=models.CASCADE, null=True)
    is_pending = models.BooleanField(default=False)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "payment_bank_transfer_history"

class BankTransferRefund(models.Model):
    history = models.OneToOneField(History, on_delete=models.CASCADE, related_name='bank_transfer_refund')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='bank_transfer_refund')
    bank_account_number = models.CharField(max_length=32)
    amount = models.FloatField()

    class Meta:
        db_table = "payment_bank_transfer_refund"

class PaymentAuction(models.Model):

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='payment_auction')
    charge_amount = models.FloatField()
    refund_amount = models.FloatField()
    history = models.OneToOneField(History, on_delete=models.CASCADE, related_name='payment_auction')
    wallet_type = models.IntegerField(null=True)

    class Meta:
        db_table = 'payment_auction'

class HistoryPending(models.Model):
    history = models.ForeignKey(History, on_delete=models.CASCADE, related_name='history')
    history_pending = models.OneToOneField(History, on_delete=models.CASCADE, related_name='history_pending')

    class Meta:
        db_table = "payment_history_pending"

class HistoryOnePay(models.Model):
    history = models.OneToOneField(History, on_delete=models.CASCADE, related_name='history_onepay')
    sicp_registration = models.ForeignKey(SICPRegistration, on_delete=models.CASCADE, null=True)
    profile_features_buyer = models.ForeignKey(ProfileFeaturesBuyer, on_delete=models.CASCADE, null=True)
    profile_features_supplier = models.ForeignKey(ProfileFeaturesSupplier, on_delete=models.CASCADE, null=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=True)
    notes = models.TextField(null=True, blank=True)
    diamond_sponsor = models.ForeignKey(UserDiamondSponsor, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "payment_history_one_pay"

class UserDiamondSponsorPayment(models.Model):
    user_diamond_sponsor = models.ForeignKey(UserDiamondSponsor, on_delete=models.CASCADE, related_name='user_diamond_sponsor_payment')
    charge_amount = models.FloatField()
    history = models.OneToOneField(History, on_delete=models.CASCADE, related_name='user_diamond_sponsor_payment')
    method_payment = models.IntegerField(null=True)

    class Meta:
        db_table = 'payment_user_diamond_sponsor'
