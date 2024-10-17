import os

from apps.master_data.models import Category, ContractType, PaymentTerm, DeliveryTerm, Currency, UnitofMeasure, TechnicalWeighting, AuctionType
from apps.rfx.models import RFXData
from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel

User = get_user_model()

# Auctions
AUCTION_STATUS_CHOICES = (
    (1, 'draft'),
    (2, 'not-start'),
    (3, 'running'),
    (4, 'on-process'),
    (5, 'awarded'),
    (6, 'cancelled')
)

SPLIT_ORDER_CHOICES = ((1, 'Award to only one supplier'), (2, 'Slip order to ward multiple suppliers'))
NEGOTIATION_AFTER_OBE_CHOICES = ((1, 'With negotiation after OBE'), (2, 'Without negotiation after OBE'))


def other_requirement_directory_path(instance, filename):
    return os.path.join(str(instance.auction.user.id), "{}.{}".format('other_requirement', filename.split('.')[-1]))


def general_term_condition_path(instance, filename):
    return os.path.join(str(instance.auction.user.id), "{}.{}".format('general_term_condition', filename.split('.')[-1]))

class Auction(TimeStampedModel, models.Model):
    item_code = models.CharField(max_length=8, unique=True)
    title = models.CharField(max_length=255)
    budget = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    extend_time = models.DateTimeField(null=True)
    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE)
    contract_from = models.DateTimeField(blank=True, null=True)
    contract_to = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.CASCADE)
    delivery_term = models.ForeignKey(DeliveryTerm, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=1024)
    general_term_condition = models.FileField(upload_to=general_term_condition_path, null=True)
    other_requirement = models.FileField(upload_to=other_requirement_directory_path, null=True)
    note_from_buyer = models.CharField(max_length=1024, null=True, blank=True)
    technical_weighting = models.ForeignKey(TechnicalWeighting, on_delete=models.CASCADE)
    auction_type1 = models.ForeignKey(AuctionType, on_delete=models.CASCADE, related_name='auction_type_1')
    auction_type2 = models.ForeignKey(AuctionType, on_delete=models.CASCADE, related_name='auction_type_2', null=True)
    status = models.PositiveSmallIntegerField(choices=AUCTION_STATUS_CHOICES, null=False, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    reasons = models.TextField(max_length=6500, null=True, blank=True)
    number_of_times_triggered = models.IntegerField(default=0)
    coupon = models.TextField(null=True)
    split_order = models.PositiveSmallIntegerField(choices=SPLIT_ORDER_CHOICES, default=1)
    auction_next_round = models.OneToOneField("Auction", on_delete=models.CASCADE, related_name="auction_next_rounds", null=True)
    negotiation_after_obe = models.PositiveSmallIntegerField(choices=NEGOTIATION_AFTER_OBE_CHOICES, default=1)
    auction_rules = models.CharField(max_length=1024, null=True, blank=True)
    rfx = models.ForeignKey(RFXData, on_delete=models.CASCADE, related_name="auction_rfxs", null=True, blank=True)

    class Meta:
        db_table = 'auction'

    def get_options(self):
        options = None
        if self.auction_type1_id == 1:
            options = AuctionTypeTrafficLight.objects.get(auction_id=self.id)
        if self.auction_type1_id == 2:
            options = AuctionTypeSealedBid.objects.get(auction_id=self.id)
        if self.auction_type1_id == 3:
            options = AuctionTypeRanking.objects.get(auction_id=self.id)
        if self.auction_type1_id == 4:
            options = AuctionTypePrices.objects.get(auction_id=self.id)
        if self.auction_type1_id == 5:
            options = AuctionTypeDutch.objects.get(auction_id=self.id)
        if self.auction_type1_id == 6:
            options = AuctionTypeJapanese.objects.get(auction_id=self.id)
        return options

    def get_configuration(self):
        configuration = None

        if self.auction_type1 == 1:
            configuration = AuctionTypeTrafficLight.objects.get(pk=self.id)

        return configuration

class AuctionGeneralTermCondition(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='general_term_conditions')
    general_term_condition = models.FileField(upload_to=general_term_condition_path)

    class Meta:
        db_table = 'auction_general_term_condition'

class AuctionOtherRequirement(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='other_requirements')
    other_requirement = models.FileField(upload_to=other_requirement_directory_path)

    class Meta:
        db_table = 'auction_other_requirement'

class AuctionItem(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    budget = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField()
    unit = models.ForeignKey(UnitofMeasure, on_delete=models.CASCADE, related_name='unit')
    price_yellow = models.FloatField(null=True, blank=True)
    target_price = models.FloatField(null=True, blank=True)
    minimum_bid_step = models.FloatField(null=True, blank=True)
    maximum_bid_step = models.FloatField(null=True)
    max_price = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'auction_item'

SUPPLIER_STATUS_CHOICES = (
    (1, 'Awaiting'),
    (2, 'Deposited'),
    (3, 'Cancelled'),
    (4, 'Partial'),
    (5, 'Ready'),
    (6, 'Awaiting award'),
    (7, 'Withdraw'),
    (8, 'Awaiting refunding request'),
    (9, 'Request refunding'),
    (10, 'Refunded'),
    (11, 'Submitted'),
)

SUPPLIER_AWARDED = ((1, 'awarded'), (2, 'rejected'), (3, 'auction cancelled'))


class AuctionSupplier(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='suppliers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier_status = models.PositiveSmallIntegerField(choices=SUPPLIER_STATUS_CHOICES, null=False, default=1)
    is_accept = models.BooleanField(default=False)
    awarded = models.PositiveSmallIntegerField(choices=SUPPLIER_AWARDED, null=True, blank=True)
    reasons = models.TextField(max_length=6500, null=True, blank=True)
    note_from_supplier = models.CharField(max_length=1024, null=True, blank=True)
    email_reminder_deposit = models.DateTimeField(null=True, default=None)
    is_accept_rule = models.BooleanField(default=False)

    class Meta:
        db_table = 'auction_supplier'

class AuctionItemSupplier(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    auction_supplier = models.ForeignKey(AuctionSupplier, on_delete=models.CASCADE, related_name='items')
    auction_item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name='suppliers')
    price = models.FloatField()
    technical_score = models.FloatField(null=True)
    confirm_price = models.FloatField(null=True)

    class Meta:
        db_table = 'auction_item_supplier'

class AuctionEmail(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'auction_email'


class AuctionBid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)
    price = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auction_bid'

class AuctionResult(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    class Meta:
        db_table = 'auction_result'

AUCTION_EXTENSION_CHOICES = ((1, 'Auction is controlled by buyer'), (2, 'Automatic extension'))

AUTOMATIC_EXTENSION_CHOICES = ((1, 'New bid in trigger time'), (2, 'New bid among the best rankings'), (3, 'Equal new best bids'))

MAX_PRICE_TYPE_CHOICES = ((1, 'Maximum price for entire Auction'), (2, 'Maximum price per position'))

TYPE_OF_BIDDING_CHOICES = ((1, 'Bidder must underbid himself'), (2, 'Bidder must underbid the best bid'))

VIEWS_DISABLED_CHOICES = ((1, 'permanent'), (2, 'in the last minutes'))

INDIVIDUAL_OR_MAX_PRICE_CHOICE = ((1, 'Individual max prices per supplier'), (2, 'Maximum price must not be reached'))


class AuctionTypeTrafficLight(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='auction_type_traffic_light')
    max_price_settings = models.BooleanField()
    max_price_type = models.PositiveSmallIntegerField(choices=MAX_PRICE_TYPE_CHOICES, null=True, blank=True)
    individual_or_max_price = models.PositiveSmallIntegerField(choices=INDIVIDUAL_OR_MAX_PRICE_CHOICE, null=True, blank=True)
    hide_target_price = models.BooleanField(default=True)
    type_of_bidding = models.PositiveSmallIntegerField(choices=TYPE_OF_BIDDING_CHOICES, null=False)
    type_of_bid_monitoring1 = models.BooleanField(null=True)
    type_of_bid_monitoring2 = models.BooleanField(null=True)
    type_of_bid_monitoring3 = models.BooleanField(null=True)
    type_of_bid_monitoring5 = models.BooleanField(null=True)
    type_of_bid_monitoring6 = models.BooleanField(null=True)
    views_disabled = models.PositiveSmallIntegerField(choices=VIEWS_DISABLED_CHOICES, null=True, blank=True)
    minutes = models.IntegerField(null=True, blank=True)
    auction_extension = models.PositiveSmallIntegerField(choices=AUCTION_EXTENSION_CHOICES, null=True, blank=True)
    auction_extension_trigger = models.PositiveSmallIntegerField(choices=AUTOMATIC_EXTENSION_CHOICES, null=True, blank=True)
    number_of_rankings = models.IntegerField(null=True, blank=True)
    frequency = models.IntegerField(null=True, blank=True)
    trigger_time = models.IntegerField(null=True, blank=True)
    prolongation_by = models.IntegerField(null=True, blank=True)
    entire_auction = models.FloatField(null=True, blank=True)
    warning_minutes = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'auction_type_traffic_light'

# Explain all type of bid mornitoring:
# -----------------------------------------------------------------------------------------
# Type of bid mornitoring 1: Bidder sees a ranking
# Type of bid mornitoring 2: Only best bidder can see his rank
# Type of bid mornitoring 3: Bidder sees the best bid
# Type of bid mornitoring 4: Other bids are visible before submission of an initial bid (delete this option)
# Type of bid mornitoring 5: Suppliers are invisible to the buyer during the auction
# Type of bid mornitoring 6: View of competitor's information is disabled
# ------------------------------------------------------------------------------------------
# Traffic Light and Ranking are the same, have 5 above types
# Prices has 3 types of bid mornitoring: include 1, 5, 6 (see meanings as above).


class AuctionTypeSealedBid(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='auction_type_sealed_bid')
    type_of_bid_monitoring6 = models.BooleanField(null=True, default=True)
    views_disabled = models.PositiveSmallIntegerField(choices=VIEWS_DISABLED_CHOICES, default=1)
    auction_extension = models.PositiveSmallIntegerField(choices=AUCTION_EXTENSION_CHOICES, default=1)
    warning_minutes = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'auction_type_sealed_bid'

class AuctionTypeRanking(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='auction_type_ranking')
    max_price_settings = models.BooleanField()
    max_price_type = models.PositiveSmallIntegerField(choices=MAX_PRICE_TYPE_CHOICES, null=True, blank=True)
    individual_or_max_price = models.PositiveSmallIntegerField(choices=INDIVIDUAL_OR_MAX_PRICE_CHOICE, null=True, blank=True)
    hide_target_price = models.BooleanField(default=True)
    type_of_bidding = models.PositiveSmallIntegerField(choices=TYPE_OF_BIDDING_CHOICES, null=False)
    type_of_bid_monitoring1 = models.BooleanField(null=True)
    type_of_bid_monitoring2 = models.BooleanField(null=True, default=True)
    type_of_bid_monitoring3 = models.BooleanField(null=True)
    type_of_bid_monitoring5 = models.BooleanField(null=True)
    type_of_bid_monitoring6 = models.BooleanField(null=True)
    views_disabled = models.PositiveSmallIntegerField(choices=VIEWS_DISABLED_CHOICES, null=True, blank=True)
    minutes = models.IntegerField(null=True, blank=True)
    auction_extension = models.PositiveSmallIntegerField(choices=AUCTION_EXTENSION_CHOICES, null=True, blank=True)
    auction_extension_trigger = models.PositiveSmallIntegerField(choices=AUTOMATIC_EXTENSION_CHOICES, null=True, blank=True)
    number_of_rankings = models.IntegerField(null=True, blank=True)
    frequency = models.IntegerField(null=True, blank=True)
    trigger_time = models.IntegerField(null=True, blank=True)
    prolongation_by = models.IntegerField(null=True, blank=True)
    entire_auction = models.FloatField(null=True, blank=True)
    warning_minutes = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'auction_type_ranking'

class AuctionTypePrices(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='auction_type_prices')
    max_price_settings = models.BooleanField()
    max_price_type = models.PositiveSmallIntegerField(choices=MAX_PRICE_TYPE_CHOICES, null=True, blank=True)
    individual_or_max_price = models.PositiveSmallIntegerField(choices=INDIVIDUAL_OR_MAX_PRICE_CHOICE, null=True, blank=True)
    hide_target_price = models.BooleanField(default=True)
    type_of_bidding = models.PositiveSmallIntegerField(choices=TYPE_OF_BIDDING_CHOICES, null=False)
    type_of_bid_monitoring1 = models.BooleanField(null=True)
    type_of_bid_monitoring5 = models.BooleanField(null=True)
    type_of_bid_monitoring6 = models.BooleanField(null=True)
    views_disabled = models.PositiveSmallIntegerField(choices=VIEWS_DISABLED_CHOICES, null=True, blank=True)
    minutes = models.IntegerField(null=True, blank=True)
    auction_extension = models.PositiveSmallIntegerField(choices=AUCTION_EXTENSION_CHOICES, null=True, blank=True)
    auction_extension_trigger = models.PositiveSmallIntegerField(choices=AUTOMATIC_EXTENSION_CHOICES, null=True, blank=True)
    number_of_rankings = models.IntegerField(null=True, blank=True)
    frequency = models.IntegerField(null=True, blank=True)
    trigger_time = models.IntegerField(null=True, blank=True)
    prolongation_by = models.IntegerField(null=True, blank=True)
    entire_auction = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'auction_type_prices'

class AuctionTypeDutch(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='auction_type_dutch')
    initial_price = models.FloatField()
    end_price = models.FloatField()
    price_step = models.FloatField()
    price_validity = models.FloatField()
    round_auction = models.IntegerField(default=1)

    class Meta:
        db_table = 'auction_type_dutch'

class AuctionTypeJapanese(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='auction_type_japanese')
    initial_price = models.FloatField()
    end_price = models.FloatField()
    price_step = models.FloatField()
    price_validity = models.FloatField()
    round_auction = models.IntegerField(default=1)

    class Meta:
        db_table = 'auction_type_japanese'

class AuctionAward(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='auction_award')
    auction_item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name='auction_award_item')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction_award_supplier')
    percentage = models.FloatField()
    price = models.FloatField()
    platform_fee = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auction_award'
