import operator
import pytz

from apps.auctions.models import (
    Auction,
    AuctionItem,
    AuctionSupplier,
    AuctionItemSupplier,
    AuctionBid,
    AuctionTypeTrafficLight,
    AuctionTypeRanking,
    AuctionTypePrices,
    AuctionTypeSealedBid,
    AuctionTypeDutch,
    AuctionTypeJapanese,
    AuctionGeneralTermCondition,
    AuctionOtherRequirement,
    AuctionAward,
)
from apps.master_data.models import Coupon
from apps.payment.models import PaymentAuction
from apps.users.models import Buyer, Supplier
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Max, Min
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber
from rest_framework import serializers

User = get_user_model()

class AuctionBidSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    auction_item_id = serializers.IntegerField()
    company_full_name = serializers.ReadOnlyField(source='user.supplier.company_full_name')

    class Meta:
        model = AuctionBid
        fields = ('id', 'auction_id', 'user_id', 'auction_item_id', 'price', 'created', 'company_full_name')

    def create(self, data):
        data.pop('company_full_name')
        return super().create(self, data)

class AuctionSupplierSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = AuctionSupplier
        fields = ('id', 'auction_id', 'user_id', 'supplier_status', 'is_accept', 'note_from_supplier', 'is_accept_rule')

class AuctionItemSupplierSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()
    auction_item_id = serializers.IntegerField()
    auction_supplier_id = serializers.IntegerField()

    user_id = serializers.SerializerMethodField()
    company_full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username =  serializers.SerializerMethodField()

    class Meta:
        model = AuctionItemSupplier
        fields = (
            'id',
            'auction_id',
            'auction_item_id',
            'auction_supplier_id',
            'price',
            'confirm_price',
            'technical_score',
            'user_id',
            'company_full_name',
            'email',
            'username',
        )

    def get_user_id(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(id=obj.auction_supplier_id).last()

        if auctionSupplier:
            return auctionSupplier.user_id
        else:
            return None

    def get_company_full_name(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(id=obj.auction_supplier_id).last()

        profile = auctionSupplier.user.get_profile()

        return profile.company_full_name

    def get_email(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(id=obj.auction_supplier_id).last()
        return auctionSupplier.user.email

    def get_username(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(id=obj.auction_supplier_id).last()
        return auctionSupplier.user.username

class AuctionItemSerializer(serializers.ModelSerializer):
    suppliers = serializers.SerializerMethodField()
    auction_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()

    class Meta:
        model = AuctionItem
        fields = (
            'id',
            'auction_id',
            'name',
            'budget',
            'quantity',
            'unit_id',
            'suppliers',
            'price_yellow',
            'target_price',
            'minimum_bid_step',
            'maximum_bid_step',
            'max_price',
            'description',
        )

    def get_suppliers(self, instance):
        suppliers = instance.suppliers.all().order_by('id')
        return AuctionItemSupplierSerializer(suppliers, many=True, read_only=True).data

class AuctionItemBySupplierSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()
    price = serializers.SerializerMethodField()
    confirm_price = serializers.SerializerMethodField()

    class Meta:
        model = AuctionItem
        fields = (
            'id',
            'auction_id',
            'name',
            'budget',
            'quantity',
            'unit_id',
            'price_yellow',
            'target_price',
            'minimum_bid_step',
            'maximum_bid_step',
            'max_price',
            'price',
            'confirm_price',
            'description',
        )

    def get_price(self, obj):

        auction_supplier = AuctionSupplier.objects.filter(user_id=self.context['request'].user.id, auction_id=obj.auction_id).last()

        if auction_supplier is not None:
            auction_item_supplier = AuctionItemSupplier.objects.filter(
                auction_id=obj.auction_id, auction_item_id=obj.id, auction_supplier_id=auction_supplier.id
            ).last()

            return auction_item_supplier.price

        return 0

    def get_confirm_price(self, obj):

        auction_supplier = AuctionSupplier.objects.filter(user_id=self.context['request'].user.id, auction_id=obj.auction_id).last()

        if auction_supplier is not None:
            auction_item_supplier = AuctionItemSupplier.objects.filter(
                auction_id=obj.auction_id, auction_item_id=obj.id, auction_supplier_id=auction_supplier.id
            ).last()

            return auction_item_supplier.confirm_price
        return 0

class AuctionGeneralTermConditionSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionGeneralTermCondition
        fields = ('id', 'auction_id', 'general_term_condition')

class AuctionOtherRequirementSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionOtherRequirement
        fields = ('id', 'auction_id', 'other_requirement')

class AuctionSerializer(serializers.ModelSerializer):
    suppliers = AuctionSupplierSerializer(many=True, read_only=True)
    user_id = serializers.IntegerField()
    other_requirements = AuctionOtherRequirementSerializer(many=True, read_only=True)
    general_term_conditions = AuctionGeneralTermConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'item_code',
            'budget',
            'currency',
            'category',
            'start_time',
            'end_time',
            'extend_time',
            'contract_type',
            'contract_from',
            'contract_to',
            'delivery_date',
            'payment_term',
            'delivery_term',
            'delivery_address',
            'general_term_conditions',
            'other_requirements',
            'note_from_buyer',
            'technical_weighting',
            'auction_type1',
            'auction_type2',
            'status',
            'suppliers',
            'user_id',
            'number_of_times_triggered',
            'created',
            'coupon',
            'split_order',
            'auction_next_round',
            'auction_rules',
            'negotiation_after_obe',
        )

# ------------------For--E-Auction-Type---------------------------------
class AuctionTypeTrafficLightSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionTypeTrafficLight
        fields = (
            'id',
            'auction_id',
            'max_price_settings',
            'max_price_type',
            'individual_or_max_price',
            'hide_target_price',
            'type_of_bidding',
            'type_of_bid_monitoring1',
            'type_of_bid_monitoring2',
            'type_of_bid_monitoring3',
            'type_of_bid_monitoring5',
            'type_of_bid_monitoring6',
            'views_disabled',
            'minutes',
            'auction_extension',
            'auction_extension_trigger',
            'number_of_rankings',
            'frequency',
            'trigger_time',
            'prolongation_by',
            'entire_auction',
            'warning_minutes',
        )

class AuctionTypeRankingSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionTypeRanking
        fields = (
            'id',
            'auction_id',
            'max_price_settings',
            'max_price_type',
            'individual_or_max_price',
            'hide_target_price',
            'type_of_bidding',
            'type_of_bid_monitoring1',
            'type_of_bid_monitoring2',
            'type_of_bid_monitoring3',
            'type_of_bid_monitoring5',
            'type_of_bid_monitoring6',
            'views_disabled',
            'minutes',
            'auction_extension',
            'auction_extension_trigger',
            'number_of_rankings',
            'frequency',
            'trigger_time',
            'prolongation_by',
            'entire_auction',
            'warning_minutes',
        )

class AuctionTypePricesSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionTypePrices
        fields = (
            'id',
            'auction_id',
            'max_price_settings',
            'max_price_type',
            'individual_or_max_price',
            'hide_target_price',
            'type_of_bidding',
            'type_of_bid_monitoring1',
            'type_of_bid_monitoring5',
            'type_of_bid_monitoring6',
            'views_disabled',
            'minutes',
            'auction_extension',
            'auction_extension_trigger',
            'number_of_rankings',
            'frequency',
            'trigger_time',
            'prolongation_by',
            'entire_auction',
        )

class AuctionTypeSealedBidSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionTypeSealedBid
        fields = ('id', 'auction_id', 'type_of_bid_monitoring6', 'views_disabled', 'auction_extension', 'warning_minutes')

class AuctionTypeDutchSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionTypeDutch
        fields = (
            'id',
            'auction_id',
            'initial_price',
            'end_price',
            'price_step',
            'price_validity',
            'round_auction',
        )

class AuctionTypeJapaneseSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()

    class Meta:
        model = AuctionTypeJapanese
        fields = (
            'id',
            'auction_id',
            'initial_price',
            'end_price',
            'price_step',
            'price_validity',
            'round_auction',
        )

class AuctionBySupplierSerializer(serializers.ModelSerializer):

    supplier_status = serializers.SerializerMethodField()
    user_id = serializers.IntegerField()
    other_requirements = AuctionOtherRequirementSerializer(many=True, read_only=True)
    general_term_conditions = AuctionGeneralTermConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'item_code',
            'budget',
            'currency',
            'category',
            'start_time',
            'end_time',
            'extend_time',
            'contract_type',
            'contract_from',
            'contract_to',
            'delivery_date',
            'payment_term',
            'delivery_term',
            'delivery_address',
            'general_term_conditions',
            'other_requirements',
            'note_from_buyer',
            'technical_weighting',
            'auction_type1',
            'auction_type2',
            'status',
            'supplier_status',
            'user_id',
            'number_of_times_triggered',
            'created',
            'split_order',
            'auction_next_round',
            'negotiation_after_obe',
            'auction_rules'
        )

    def get_supplier_status(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(user_id=self.context['request'].user.id, auction_id=obj.id).last()

        if auctionSupplier:
            return auctionSupplier.supplier_status

        else:
            return None

class AuctionDetailSerializer(serializers.ModelSerializer):

    items = AuctionItemSerializer(many=True, read_only=True)
    bids = AuctionBidSerializer(many=True, read_only=True)
    user_id = serializers.IntegerField()
    rating = serializers.SerializerMethodField()
    company_full_name = serializers.SerializerMethodField()
    notes_from_supplier = serializers.SerializerMethodField()
    other_requirements = AuctionOtherRequirementSerializer(many=True, read_only=True)
    general_term_conditions = AuctionGeneralTermConditionSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    suppliers = serializers.SerializerMethodField()
    is_next_round =serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'item_code',
            'budget',
            'currency',
            'category',
            'start_time',
            'end_time',
            'extend_time',
            'contract_type',
            'contract_from',
            'contract_to',
            'delivery_date',
            'payment_term',
            'delivery_term',
            'delivery_address',
            'general_term_conditions',
            'other_requirements',
            'note_from_buyer',
            'technical_weighting',
            'auction_type1',
            'auction_type2',
            'status',
            'user_id',
            'company_full_name',
            'number_of_times_triggered',
            'created',
            'items',
            'bids',
            'rating',
            'notes_from_supplier',
            'coupon',
            'split_order',
            'auction_next_round',
            'full_name',
            'negotiation_after_obe',
            'auction_rules',
            'suppliers',
            "is_next_round",
        )

    def get_notes_from_supplier(self, obj):
        results = []
        auction_suppliers = AuctionSupplier.objects.filter(auction_id=obj.id)
        for auction_supplier in auction_suppliers:
            supplier = Supplier.objects.get(user_id=auction_supplier.user_id)
            company_full_name = supplier.company_full_name
            note = auction_supplier.note_from_supplier
            if note is not None:
                results.append({'company_full_name': company_full_name, 'note_from_supplier': note})
        return results

    def get_rating(self, obj):
        items = obj.items.all()

        bids = []

        for item in items:
            item_bids = (
                AuctionBid.objects.filter(auction_id=obj.id, auction_item_id=item.id)
                .values('auction_id', 'auction_item_id', 'user_id')
                .annotate(min_price=Min('price'), bid_id=Max('id'), ranking=Window(expression=RowNumber(), order_by=(Min('price'), Max('id'))))
                .order_by('ranking')
            )

            for item_bid in item_bids:
                bids.append(item_bid)

        return bids

    def get_company_full_name(self, obj):
        user = Buyer.objects.get(user_id=obj.user_id)
        return user.company_full_name

    def get_full_name(self, obj):
        user = User.objects.get(id=obj.user_id)
        return user.full_name

    def get_suppliers(self, instance):
        suppliers = instance.suppliers.all().order_by('id')
        return AuctionSupplierSerializer(suppliers, many=True, read_only=True).data
        
    def get_is_next_round(self, obj):
        return Auction.objects.filter(auction_next_round=obj).exists()

class AuctionDetailTrafficLightSerializer(serializers.ModelSerializer):

    items = AuctionItemSerializer(many=True, read_only=True)
    bids = AuctionBidSerializer(many=True, read_only=True)
    options = AuctionTypeTrafficLightSerializer(read_only=True)
    user_id = serializers.IntegerField()
    other_requirements = AuctionOtherRequirementSerializer(many=True, read_only=True)
    general_term_conditions = AuctionGeneralTermConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'item_code',
            'budget',
            'currency',
            'category',
            'start_time',
            'end_time',
            'extend_time',
            'number_of_times_triggered',
            'contract_type',
            'contract_from',
            'contract_to',
            'delivery_date',
            'payment_term',
            'delivery_term',
            'delivery_address',
            'general_term_conditions',
            'other_requirements',
            'note_from_buyer',
            'technical_weighting',
            'auction_type1',
            'auction_type2',
            'status',
            'user_id',
            'created',
            'items',
            'bids',
            'options',
            'coupon',
            'split_order',
            'auction_next_round',
            'negotiation_after_obe',
            'auction_rules',
        )


class AuctionDetailBySupplierSerializer(serializers.ModelSerializer):
    supplier_status = serializers.SerializerMethodField()
    is_accept = serializers.SerializerMethodField()

    user_id = serializers.IntegerField()
    items = AuctionItemBySupplierSerializer(many=True, read_only=True)
    bids = AuctionBidSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    company_full_name = serializers.SerializerMethodField()
    other_requirements = AuctionOtherRequirementSerializer(many=True, read_only=True)
    general_term_conditions = AuctionGeneralTermConditionSerializer(many=True, read_only=True)
    buyer_full_name = serializers.SerializerMethodField()
    rating_total = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'item_code',
            'budget',
            'currency',
            'category',
            'start_time',
            'end_time',
            'extend_time',
            'number_of_times_triggered',
            'contract_type',
            'contract_from',
            'contract_to',
            'delivery_date',
            'payment_term',
            'delivery_term',
            'delivery_address',
            'general_term_conditions',
            'other_requirements',
            'note_from_buyer',
            'technical_weighting',
            'auction_type1',
            'auction_type2',
            'status',
            'supplier_status',
            'user_id',
            'company_full_name',
            'created',
            'items',
            'bids',
            'rating',
            'split_order',
            'auction_next_round',
            'is_accept',
            'buyer_full_name',
            'negotiation_after_obe',
            'auction_rules',
            'rating_total',
        )

    def get_supplier_status(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(user_id=self.context['request'].user.id, auction_id=obj.id).last()
        if auctionSupplier:
            return auctionSupplier.supplier_status

        else:
            return None

    def get_is_accept(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(user_id=self.context['request'].user.id, auction_id=obj.id).last()
        if auctionSupplier:
            return auctionSupplier.is_accept

        else:
            return None

    def get_rating(self, obj):
        items = obj.items.all()
        bids = []
        for item in items:
            item_bids = (
                AuctionBid.objects.filter(auction_id=obj.id, auction_item_id=item.id)
                .values('auction_id', 'auction_item_id', 'user_id')
                .annotate(min_price=Min('price'), bid_id=Max('id'), ranking=Window(expression=RowNumber(), order_by=(Min('price'), Max('id'))))
                .order_by('ranking')
            )

            for item_bid in item_bids:
                bids.append(item_bid)

        return bids

    def get_company_full_name(self, obj):
        user = Buyer.objects.get(user_id=obj.user_id)
        return user.company_full_name

    def get_buyer_full_name(self, obj):
        user = User.objects.get(id=obj.user_id)
        return user.full_name

    def get_rating_total(self, obj):
        auction_item = AuctionItem.objects.filter(auction=obj)
        auction_supplier = AuctionSupplier.objects.filter(auction=obj, is_accept=True, supplier_status__in=[5, 6, 8, 9, 10]).order_by('id')
        list_total_bid = []
        for supplier in auction_supplier:
            total_bid = 0
            for item in auction_item:
                auction_bids = AuctionBid.objects.filter(user=supplier.user, auction_item=item).order_by('id')
                auction_item_supplier = AuctionItemSupplier.objects.filter(auction_item=item, auction_supplier=supplier).first()
                if auction_bids.exists():
                    price = auction_bids.last().price
                else:
                    price = auction_item_supplier.confirm_price
                total_bid += price
            list_total_bid.append({"user_id": supplier.user_id, "total_bid": total_bid})
        total_bid_list = []
        for supplier in list_total_bid:
            total_bid_list.append(supplier.get("total_bid"))
        ratings = sorted(list_total_bid, key=operator.itemgetter("total_bid"))
        return ratings

# ----For---E-Auction--Result----------------------------------------------------------------------
class AuctionItemSupplierResultSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()
    auction_item_id = serializers.IntegerField()
    auction_supplier_id = serializers.IntegerField()
    user_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    price_last_bid = serializers.SerializerMethodField()

    class Meta:
        model = AuctionItemSupplier
        fields = (
            'id',
            'auction_id',
            'auction_item_id',
            'name',
            'budget',
            'auction_supplier_id',
            'price',
            'technical_score',
            'user_id',
            'price_last_bid',
        )

    def get_user_id(self, obj):
        auctionSupplier = AuctionSupplier.objects.filter(id=obj.auction_supplier_id).last()

        if auctionSupplier:
            return auctionSupplier.user_id
        else:
            return None

    def get_name(self, obj):
        auctionItem = AuctionItem.objects.filter(id=obj.auction_item_id).last()

        if auctionItem:
            return auctionItem.name
        else:
            return None

    def get_price_last_bid(self, obj):

        auctionBid = (
            AuctionBid.objects.annotate(Max('id'))
            .filter(auction_id=obj.auction_id, auction_item_id=obj.auction_item_id, user_id=self.get_user_id(obj))
            .last()
        )

        if auctionBid:
            return auctionBid.price
        else:
            return None


class AuctionSupplierResultSerializer(serializers.ModelSerializer):
    auction_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    items = AuctionItemSupplierResultSerializer(many=True, read_only=True)

    class Meta:
        model = AuctionSupplier
        fields = (
            'id',
            'auction_id',
            'user_id',
            'items',
            'awarded',
            'reasons',
        )


class AuctionResultsSerializer(serializers.ModelSerializer):

    suppliers = AuctionSupplierResultSerializer(many=True, read_only=True)
    other_requirements = AuctionOtherRequirementSerializer(many=True, read_only=True)
    general_term_conditions = AuctionGeneralTermConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'start_time',
            'end_time',
            'number_of_times_triggered',
            'status',
            'reasons',
            'payment_term',
            'delivery_term',
            'delivery_address',
            'general_term_conditions',
            'other_requirements',
            'technical_weighting',
            'created',
            'suppliers',
            'split_order',
            'auction_next_round',
            'negotiation_after_obe',
            'auction_rules',
        )


class GetAuctionSerializer(serializers.ModelSerializer):
    suppliers = serializers.SerializerMethodField()
    user_id = serializers.IntegerField()
    username = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    company_full_name = serializers.SerializerMethodField()
    other_requirements = AuctionOtherRequirementSerializer(many=True, read_only=True)
    general_term_conditions = AuctionGeneralTermConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'item_code',
            'budget',
            'currency',
            'category',
            'start_time',
            'end_time',
            'extend_time',
            'contract_type',
            'contract_from',
            'contract_to',
            'delivery_date',
            'payment_term',
            'delivery_term',
            'delivery_address',
            'general_term_conditions',
            'other_requirements',
            'note_from_buyer',
            'technical_weighting',
            'auction_type1',
            'auction_type2',
            'status',
            'suppliers',
            'user_id',
            'username',
            'full_name',
            'company_full_name',
            'number_of_times_triggered',
            'created',
            'coupon',
            'split_order',
            'auction_next_round',
            'negotiation_after_obe',
            'auction_rules'
        )

    def get_suppliers(self, instance):
        suppliers = instance.suppliers.all().order_by('id')
        return AuctionSupplierSerializer(suppliers, many=True, read_only=True).data

    def get_company_full_name(self, obj):
        if self.context['request'].user.user_type == 1:
            user = Buyer.objects.get(user_id=obj.user_id)
            return user.company_full_name
        else:
            return None

    def get_username(self, obj):
        if self.context['request'].user.user_type == 1:
            user = User.objects.get(pk=obj.user_id)
            return user.username
        else:
            return None

    def get_full_name(self, obj):
        if self.context['request'].user.user_type == 1:
            user = User.objects.get(pk=obj.user_id)
            return user.full_name
        else:
            return None


def count_next_round(auction, count):
    auction = Auction.objects.filter(auction_next_round=auction)
    if not auction.exists():
        return count
    else:
        count += 1
        return count_next_round(auction.first(), count)


class AuctionReportExportSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='user.full_name')
    username = serializers.ReadOnlyField(source='user.username')
    category = serializers.ReadOnlyField(source='category.name')
    currency = serializers.ReadOnlyField(source='currency.name')
    auction_type = serializers.SerializerMethodField()
    company_full_name = serializers.ReadOnlyField(source='user.buyer.company_full_name')
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()
    rejected = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    invited = serializers.SerializerMethodField()
    city = serializers.ReadOnlyField(source='user.buyer.company_city')
    country = serializers.ReadOnlyField(source='user.buyer.company_country')
    country_state = serializers.ReadOnlyField(source='user.buyer.company_country_state')
    number_next_round = serializers.SerializerMethodField()
    coupon_code = serializers.SerializerMethodField()
    coupon_description = serializers.SerializerMethodField()
    coupon_commission = serializers.SerializerMethodField()
    coupon_commission_fee = serializers.SerializerMethodField()
    coupon_valid_from = serializers.SerializerMethodField()
    coupon_valid_to = serializers.SerializerMethodField()
    coupon_note = serializers.SerializerMethodField()
    coupon_email = serializers.SerializerMethodField()
    coupon_status = serializers.SerializerMethodField()

    award_date = serializers.SerializerMethodField()
    award_supplier = serializers.SerializerMethodField()
    award_order = serializers.SerializerMethodField()
    auction_fee = serializers.SerializerMethodField()
    value_before_OBE = serializers.SerializerMethodField()
    best_bid_after_OBE = serializers.SerializerMethodField()
    amount_vs_budget = serializers.SerializerMethodField()
    amount_vs_budget_percent = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'item_code',
            'budget',
            'currency',
            'category',
            'start_time',
            'end_time',
            'status',
            'username',
            'created',
            'number_next_round',
            'full_name',
            "item_code",
            'auction_type',
            'company_full_name',
            'participant',
            'rejected',
            'invited',
            'city',
            'country',
            'coupon_code',
            'coupon_description',
            'coupon_commission',
            'coupon_commission_fee',
            'coupon_valid_from',
            'coupon_valid_to',
            'coupon_note',
            'coupon_email',
            'coupon_status',
            'award_date',
            'award_supplier',
            'award_order',
            "auction_fee",
            "value_before_OBE",
            "best_bid_after_OBE",
            "amount_vs_budget",
            "amount_vs_budget_percent",
        )

    def get_auction_type(self, obj):
        return obj.auction_type1

    def get_start_time(self, obj):
        tz = pytz.timezone(obj.user.local_time)
        start_time = obj.start_time.replace(tzinfo=pytz.utc).astimezone(tz)
        return datetime.strftime(start_time, '%d-%m-%Y')

    def get_end_time(self, obj):
        tz = pytz.timezone(obj.user.local_time)
        end_time = obj.end_time.replace(tzinfo=pytz.utc).astimezone(tz)
        return datetime.strftime(end_time, '%d-%m-%Y')

    def get_participant(self, obj):
        return AuctionSupplier.objects.filter(auction=obj, is_accept=True).count()

    def get_rejected(self, obj):
        return AuctionSupplier.objects.filter(auction=obj, is_accept=False).count()

    def get_status(self, obj):
        if obj.status == 1:
            return 'Draft'
        elif obj.status == 2:
            return 'Not-start'
        elif obj.status == 3:
            return 'Running'
        elif obj.status == 4:
            return 'Finished'
        elif obj.status == 5:
            return 'Awarded'
        elif obj.status == 6:
            return 'Cancelled'
        else:
            return None

    def get_invited(self, obj):
        return AuctionSupplier.objects.filter(auction=obj).count()

    def get_number_next_round(self, obj):
        count = 0
        return count_next_round(obj, count)

    def get_coupon_code(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            return coupon.first().coupon_program
        return None

    def get_coupon_description(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            return coupon.first().coupon_program
        return None

    def get_coupon_commission(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            return coupon.first().commission
        return None

    def get_coupon_commission_fee(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        auction_award = AuctionAward.objects.filter(auction=obj)
        history_payment = PaymentAuction.objects.filter(auction=obj)
        amount = 0
        auction_award = AuctionAward.objects.filter(auction=obj)
        if auction_award and coupon:
            for auction_fee in history_payment:
                amount += auction_fee.charge_amount - auction_award.first().platform_fee * 1.1
            amount = amount / 1.1
            return "{:10,.2f}".format((amount * coupon.first().commission) / 100)
        return None

    def get_coupon_valid_from(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            return datetime.strftime(coupon.first().valid_from, '%d-%m-%Y')
        return None

    def get_coupon_valid_to(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            return datetime.strftime(coupon.first().valid_to, '%d-%m-%Y')
        return None

    def get_coupon_email(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            return coupon.first().email
        return None

    def get_coupon_status(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            if coupon.first().status:
                return "Active"
            return "InActive"
        return None

    def get_coupon_note(self, obj):
        coupon = Coupon.objects.filter(coupon_program=obj.coupon)
        if coupon.exists():
            return coupon.first().note
        return None

    def get_award_date(self, obj):
        auction_award = AuctionAward.objects.filter(auction=obj).first()
        if auction_award:
            tz = pytz.timezone(obj.user.local_time)
            date = auction_award.date.replace(tzinfo=pytz.utc).astimezone(tz)
            return datetime.strftime(date, '%d-%m-%Y')
        return None

    def get_award_supplier(self, obj):
        auction_award = AuctionAward.objects.filter(auction=obj).distinct("user")
        result = ''
        for i, supplier in enumerate(auction_award):
            if i == 0:
                result += supplier.user.full_name + " - " + supplier.user.username
            else:
                result += "\n" + supplier.user.full_name + " - " + supplier.user.username
        return result

    def get_award_order(self, obj):
        result = 0
        auction_award = AuctionAward.objects.filter(auction=obj)
        if auction_award:
            for award in auction_award:
                result += award.price
            return "{:10,.2f}".format(result)
        return None

    def get_auction_fee(self, obj):
        history_payment = PaymentAuction.objects.filter(auction=obj)
        amount = 0
        auction_award = AuctionAward.objects.filter(auction=obj)
        if auction_award:
            for auction_fee in history_payment:
                amount += auction_fee.charge_amount - auction_award.first().platform_fee * 1.1
            return "{:10,.2f}".format(amount / 1.1)
        return None

    def get_value_before_OBE(self, obj):
        supplier_acccept = AuctionSupplier.objects.filter(auction=obj, is_accept=True)
        if supplier_acccept:
            list_price = []
            for supplier in supplier_acccept:
                supplier_confirms = AuctionItemSupplier.objects.filter(auction=obj, auction_supplier=supplier)
                price = 0
                for supplier_confirm in supplier_confirms:
                    price += supplier_confirm.confirm_price
                list_price.append(price)
            return "{:10,.2f}".format(min(list_price))
        return None

    def get_best_bid_after_OBE(self, obj):
        supplier_acccept = AuctionSupplier.objects.filter(auction=obj, is_accept=True)
        if supplier_acccept:
            list_price = []
            for supplier in supplier_acccept:
                price = 0
                auction_items = AuctionItemSupplier.objects.filter(auction=obj, auction_supplier=supplier)
                for auction_item in auction_items:
                    auction_bid = AuctionBid.objects.filter(auction=obj, user=supplier.user, auction_item=auction_item.auction_item)
                    if auction_bid:
                        price += auction_bid.last().price
                    else:
                        price += auction_item.confirm_price
                list_price.append(price)
            return "{:10,.2f}".format(min(list_price))
        return None

    def get_amount_vs_budget(self, obj):
        result = 0
        auction_award = AuctionAward.objects.filter(auction=obj)
        if auction_award:
            for award in auction_award:
                result += award.price
            return "{:10,.2f}".format(result - obj.budget)
        return None

    def get_amount_vs_budget_percent(self, obj):
        result = 0
        auction_award = AuctionAward.objects.filter(auction=obj)
        if auction_award:
            for award in auction_award:
                result += award.price
            return round(((result - obj.budget) / (result + obj.budget)) * 100, 2)
        return None
