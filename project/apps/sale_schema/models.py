from django.db import models

import os

PROFILE_FEATURES_BUYER_CHOICES = ((1, 'unsecured'), (2, 'flyer'), (3, 'crew'), (4, 'captain'))


class ProfileFeaturesBuyer(models.Model):
    name = models.CharField(max_length=255)
    market_research = models.CharField(max_length=255)
    rfx_year = models.IntegerField(default=1)
    no_eauction_year = models.IntegerField(default=1)
    help_desk = models.CharField(max_length=255)
    report_year = models.IntegerField(default=1)
    sub_user_accounts = models.IntegerField(default=0)
    fee_eauction = models.FloatField(null=True)
    total_fee_year = models.FloatField(null=True)
    profile_features_type = models.PositiveSmallIntegerField(choices=PROFILE_FEATURES_BUYER_CHOICES)
    status = models.BooleanField(null=True, default=True)
    rfx_auto_nego = models.BooleanField(default=False)

    class Meta:
        db_table = 'sale_schema_profile_features_buyer'


PROFILE_FEATURES_SUPPLIER_CHOICES = (
    (1, 'basic'),
    (2, 'premium'),
    (3, 'sponsor'),
)


class ProfileFeaturesSupplier(models.Model):
    name = models.CharField(max_length=255)
    free_registration = models.CharField(max_length=255)
    quote_submiting = models.CharField(max_length=255)
    rfxr_receiving_priority = models.FloatField(null=True)
    sub_user_accounts = models.IntegerField()
    help_desk = models.CharField(max_length=255)
    flash_sale = models.IntegerField(default=1)
    product = models.IntegerField(default=1)
    report_year = models.IntegerField(default=1)
    base_rate_month = models.FloatField(null=True)
    base_rate_full_year = models.FloatField(null=True)
    profile_features_type = models.PositiveSmallIntegerField(choices=PROFILE_FEATURES_SUPPLIER_CHOICES)
    status = models.BooleanField(null=True, default=True)

    class Meta:
        db_table = 'sale_schema_profile_features_supplier'


SICP_CHOICES = ((1, 'unsecured'), (2, 'bronze'), (3, 'silver'), (4, 'gold'))


class SICPRegistration(models.Model):
    name = models.CharField(max_length=255)
    legal_status = models.FloatField(null=True)
    bank_account = models.FloatField(null=True)
    sanction_check = models.FloatField(null=True)
    certificate_management = models.FloatField(null=True)
    due_diligence = models.FloatField(null=True)
    financial_risk = models.FloatField(null=True)
    total_amount = models.FloatField(null=True)
    sicp_type = models.PositiveSmallIntegerField(choices=SICP_CHOICES)
    status = models.BooleanField(null=True, default=True)

    class Meta:
        db_table = 'sale_schema_sicp_registration'


class AuctionFee(models.Model):
    min_value = models.FloatField()
    max_value = models.FloatField()
    percentage = models.FloatField()

    class Meta:
        db_table = 'sale_schema_auction_fee'


class PlatformFee(models.Model):
    title = models.CharField(max_length=255)
    fee = models.FloatField()

    class Meta:
        db_table = 'sale_schema_platform_fee'


def our_partner_directory_path(instance, filename):
    return os.path.join(str('our_partner'), "{}.{}".format('our_partner', filename.split('.')[-1]))

def our_partner_logo_directory_path(instance, filename):
    return os.path.join(str('our_partner'), "{}.{}".format('our_partner_logo', filename.split('.')[-1]))

class OurPartner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=our_partner_directory_path)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    status = models.BooleanField(default=True)
    logo = models.ImageField(upload_to=our_partner_directory_path, null=True, blank=True)
    link = models.CharField(max_length=2084, null=True, blank=True)
    description = models.CharField(max_length=2048, null=True, blank=True)

    class Meta:
        db_table = "sale_schema_our_partner"
