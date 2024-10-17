import os
from django.db import models
from apps.master_data.models import Category, ContractType, PaymentTerm, DeliveryTerm, Currency, UnitofMeasure, Country, CountryState
from django.contrib.auth import get_user_model

User = get_user_model()

RFX_STATUS_CHOICES = (
    (1, 'draft'),
    (2, 'published'),
    (3, 'due date expire'),
    (4, 'awarded'),
    (5, 'e-auction'),
    (6, 'negotiation'),
    (7, 'completed'),
    (8, 'cancelled'),
    (9, 'confirmed')
)

RFX_QUOTES_SUBMITED_STATUS_CHOICES = (
    (1, 'waiting for quote'),
    (2, 'submited'),
    (3, 'auction'),
    (4, 'awarded'),
    (5, 'rejected'),
    (6, 'closed'),
)

RFX_TYPE_CHOICES = (
    (1, 'RFI'),
    (2, 'RFP'),
    (3, 'RFQ'),
    (4, 'PO'),
)

SEATS_CHOICES = (
    (1, 'available'),
    (2, 'full'),
)

SPLIT_ORDER_CHOICES = (
    (1, 'Award to only one supplier'),
    (2, 'Slip order to ward multiple suppliers'),
)

QUOTE_STATUS_CHOICES = (
    (1, 'full'),
    (2, 'not full'),
)

RFX_ATTACHMENT_TYPE_CHOICES = (
    (1, 'internal'),
    (2, 'external'),
)

RFX_ATTACHMENT_UPLOAD_BY_CHOICES = (
    (1, 'buyer'),
    (2, 'supplier'),
)


def general_purchasing_term_condition_path(instance, filename):
    return os.path.join(str(instance.auction.user.id), "{}.{}".format('rfx_general_purchasing_term_conditions', filename.split('.')[-1]))


def attachment_directory_path(instance, filename):
    return os.path.join(str(instance.rfx.user.id) + '_rfx_attachments', "{}.{}".format('rfx_attachments', filename.split('.')[-1]))


class RFXData(models.Model):
    item_code = models.CharField(max_length=20, unique=True)
    rfx_type = models.PositiveSmallIntegerField(choices=RFX_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    budget = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="currencies")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories", null=True, blank=True)
    due_date = models.DateTimeField()
    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE, related_name="contract_types")
    from_date = models.DateField()
    to_date = models.DateField()
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.CASCADE, related_name="payment_terms")
    delivery_term = models.ForeignKey(DeliveryTerm, on_delete=models.CASCADE, related_name="delivery_terms")
    delivery_address = models.CharField(max_length=1024)
    terms_and_conditions = models.BooleanField(null=True, blank=True)
    other_requirement = models.CharField(max_length=1024, null=True)
    note_for_supplier = models.CharField(max_length=1024, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=RFX_STATUS_CHOICES, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rfx_user_buyers')
    split_order = models.PositiveSmallIntegerField(choices=SPLIT_ORDER_CHOICES, default=1)
    rfx_next_round = models.OneToOneField("RFXData", on_delete=models.CASCADE, related_name="rfx_next_rounds", null=True)
    max_supplier = models.IntegerField(null=True)
    supplier_joined_amount = models.IntegerField(null=True)
    quote_status = models.PositiveSmallIntegerField(choices=QUOTE_STATUS_CHOICES, default=2)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    email_date = models.DateTimeField(null=True, blank=True)
    is_send = models.BooleanField(null=True, blank=True)
    is_full = models.BooleanField(null=True, blank=True, default=False)
    time_view_minutes = models.IntegerField(default=60)
    auto_negotiation = models.BooleanField(null=True, blank=True, default=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="country", null=True, blank=True, default=1)
    country_state = models.ForeignKey(CountryState, on_delete=models.CASCADE, related_name="country_state", null=True, blank=True, default=1)

    class Meta:
        db_table = 'rfx_rfxs'


class RFXItem(models.Model):
    rfx = models.ForeignKey(RFXData, models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    part_number = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField()
    unit = models.ForeignKey(UnitofMeasure, on_delete=models.CASCADE, related_name='units')
    unit_price = models.FloatField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    delivery_from = models.DateField(null=True, blank=True)
    delivery_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'rfx_item'


class RFXAttachment(models.Model):
    rfx = models.ForeignKey(RFXData, on_delete=models.CASCADE, related_name='attachments')
    attachment = models.FileField(upload_to=attachment_directory_path)
    attachment_type = models.PositiveSmallIntegerField(choices=RFX_ATTACHMENT_TYPE_CHOICES, default=2)
    upload_by = models.PositiveSmallIntegerField(choices=RFX_ATTACHMENT_UPLOAD_BY_CHOICES, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_attachments", null=True, blank=True)

    class Meta:
        db_table = 'rfx_attachment'


class RFXSupplier(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_suppliers')
    rfx = models.ForeignKey(RFXData, on_delete=models.CASCADE, related_name="rfx_suppliers")
    quote_submited_status = models.PositiveSmallIntegerField(choices=RFX_QUOTES_SUBMITED_STATUS_CHOICES)
    commercial_terms = models.BooleanField(null=True, blank=True)
    note_for_buyer = models.CharField(max_length=1024, null=True, blank=True)
    is_invited = models.BooleanField(default=False)
    seat_available = models.PositiveSmallIntegerField(choices=SEATS_CHOICES, default=1)
    sub_total = models.FloatField(default=0)
    is_joined = models.BooleanField(default=False)
    is_best_price = models.BooleanField(null=True, blank=True, default=False)
    is_confirm = models.BooleanField(default=False)

    class Meta:
        db_table = 'rfx_supplier'


class RFXItemSupplier(models.Model):
    rfx = models.ForeignKey(RFXData, on_delete=models.CASCADE, related_name="rfxs")
    rfx_supplier = models.ForeignKey(RFXSupplier, on_delete=models.CASCADE, related_name='rfx_suppliers')
    rfx_item = models.ForeignKey(RFXItem, on_delete=models.CASCADE, related_name='rfx_items')
    unit_price = models.FloatField(default=0, null=True, blank=True)
    vat_tax = models.FloatField(default=0, null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    order = models.IntegerField(default=0)
    informations = models.CharField(max_length=10000, null=True, blank=True)
    proposals = models.CharField(max_length=10000, null=True, blank=True)
    submitted_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'rfx_item_supplier'


class RFXAward(models.Model):
    rfx = models.ForeignKey(RFXData, on_delete=models.CASCADE, related_name='rfx_awards')
    rfx_item = models.ForeignKey(RFXItem, on_delete=models.CASCADE, related_name='rfx_awarded_items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rfx_awarded_suppliers')
    price = models.FloatField()
    percentage = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rfx_award'
