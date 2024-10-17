import django_filters
import graphene
import graphene_django_optimizer as gql_optimizer

from apps.auctions.models import (
    Auction,
    AuctionAward,
    AuctionItem,
    AuctionSupplier,
    AuctionBid,
    AuctionItemSupplier,
    AuctionGeneralTermCondition,
    AuctionOtherRequirement,
    AuctionTypeDutch,
    AuctionTypeJapanese,
    AuctionTypePrices,
    AuctionTypeRanking,
    AuctionTypeSealedBid,
    AuctionTypeTrafficLight,
)
from apps.core import CustomNode, CustomizeFilterConnectionField
from apps.users.models import User, Token
from apps.users.schema import UserNode
from django_filters import FilterSet, OrderingFilter, CharFilter
from graphene import relay, ObjectType, Connection
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.debug import DjangoDebug

# ---------Filter------------------
class AuctionFilter(FilterSet):
    item_code = django_filters.CharFilter(lookup_expr='icontains')
    title = django_filters.CharFilter(lookup_expr='icontains')
    start_time = django_filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name='end_time', lookup_expr='lte')
    status = django_filters.NumberFilter()
    budget_from = django_filters.NumberFilter(field_name='budget', lookup_expr='gte')
    budget_to = django_filters.NumberFilter(field_name='budget', lookup_expr='lte')
    budget = django_filters.NumberFilter()
    full_name = django_filters.CharFilter(field_name='user__full_name', lookup_expr='icontains')
    auction_type = django_filters.CharFilter(method='auction_type_filter')
    supplier_awarded = django_filters.CharFilter(method='supplier_awarded_filter')

    class Meta:
        model = Auction
        fields = ['id']

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('title', 'title'),
            ('status', 'status'),
            ('auction_type1', 'type'),
            ('start_time', 'start_time'),
            ('end_time', 'end_time'),
            ('budget', 'budget'),
            ('user__full_name', 'full_name'),
        )
    )

    def auction_type_filter(self, queryset, name, value):
        queryset = queryset.filter(auction_type1_id=value)
        return queryset

    def supplier_awarded_filter(self, queryset, name, value):
        value = value.split(',')
        list_id = map(lambda x: int(x), value)
        auction_id = map(
            lambda x: x.get('auction_id'),
            AuctionSupplier.objects.filter(user_id__in=list_id, auction__status=5, awarded=1).values('auction_id'),
        )
        queryset = queryset.filter(id__in=auction_id)
        return queryset


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length


class AuctionAwardFilter(FilterSet):
    auction_id = CharFilter(method="auction_id_filter")
    user_id = CharFilter(method="user_id_filter")

    class Meta:
        model = AuctionAward
        fields = ['id', 'percentage', 'price']

    order_by = OrderingFilter(fields=(('id', 'id'), ('percentage', 'percentage'), ('price', 'price')))

    def auction_id_filter(self, queryset, name, value):
        queryset = queryset.filter(auction_id=value)
        return queryset

    def user_id_filter(self, queryset, name, value):
        queryset = queryset.filter(user_id=value)
        return queryset


class AuctionAwardNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionAward
        filterset_class = AuctionAwardFilter
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


class AuctionItemNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionItem
        filter_fields = ['id']
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


class AuctionSupplierNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionSupplier
        filter_fields = ['id']
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


class AuctionItemSupplierNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionItemSupplier
        filter_fields = ['id']
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


class AuctionGeneralTermConditionNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionGeneralTermCondition
        filter_fields = ['id']
        convert_choices_to_enum = False

    def resolve_general_term_condition(self, info):
        if self.general_term_condition and hasattr(self.general_term_condition, 'url'):
            return info.context.build_absolute_uri(self.general_term_condition.url)
        else:
            return ''


class AuctionOtherRequirementNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionOtherRequirement
        filter_fields = ['id']
        convert_choices_to_enum = False

    def resolve_other_requirement(self, info):
        if self.other_requirement and hasattr(self.other_requirement, 'url'):
            return info.context.build_absolute_uri(self.other_requirement.url)
        else:
            return ''


class AuctionTypeDutchNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionTypeDutch
        filter_fields = ['id']
        convert_choices_to_enum = False


class AuctionTypeJapaneseNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionTypeJapanese
        filter_fields = ['id']
        convert_choices_to_enum = False


class AuctionTypePricesNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionTypePrices
        filter_fields = ['id']
        convert_choices_to_enum = False


class AuctionTypeSealedBidNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionTypeSealedBid
        filter_fields = ['id']
        convert_choices_to_enum = False


class AuctionTypeTrafficLightNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionTypeTrafficLight
        filter_fields = ['id']
        convert_choices_to_enum = False


class AuctionTypeRankingNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionTypeRanking
        filter_fields = ['id']
        convert_choices_to_enum = False


class AuctionBidNode(DjangoObjectType):
    class Meta:
        model = AuctionBid
        filter_fields = ['id']


class AuctionNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')
    is_next_round = graphene.Boolean()
    items = DjangoFilterConnectionField(AuctionItemNode)
    
    class Meta:
        model = Auction
        filterset_class = AuctionFilter
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('-id'), info)
            elif token.user.isBuyer():
                queryset = gql_optimizer.query(queryset.filter(user=token.user).order_by('-id'), info)
            elif token.user.isSupplier():
                list_id = map(
                    lambda x: x.get('auction_id'),
                    AuctionSupplier.objects.filter(user=token.user).values('auction_id'),
                )
                queryset = gql_optimizer.query(queryset.filter(id__in=list_id).exclude(status=1).order_by('-id'), info)
        except:
            queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset

    def resolve_is_next_round(self, info):
        return Auction.objects.filter(auction_next_round=self).exists()
    
    def resolve_items(self, info):
        return AuctionItem.objects.filter(auction=self)


class ItemResult(graphene.ObjectType):
    user = graphene.Field(UserNode)
    price = graphene.Float()
    confirm_price = graphene.Float()

    def resolve_user(self, info):
        return User.objects.get(id=self.get('user_id'))


class AuctionResults(graphene.ObjectType):
    auction_item = graphene.Field(AuctionItemNode)
    suppliers = graphene.List(ItemResult)
    has_next_round = graphene.Boolean()
    
    def resolve_auction_item(self, info):
        return AuctionItem.objects.get(id=self.get('auction_item_id'))

    def resolve_suppliers(self, info):
        return self.get('suppliers')

    def resolve_has_next_round(self, info):

        return self.get('has_next_round')


class ConectionResults(graphene.Connection):
    class Meta:
        node = AuctionResults

class Query(ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug')

    auction = CustomNode.Field(AuctionNode)
    auctions = CustomizeFilterConnectionField(AuctionNode)

    auction_award = CustomNode.Field(AuctionAwardNode)
    auction_awards = CustomizeFilterConnectionField(AuctionAwardNode)

    auction_item = CustomNode.Field(AuctionItemNode)
    auction_items = CustomizeFilterConnectionField(AuctionItemNode)

    auction_supplier = CustomNode.Field(AuctionSupplierNode)
    auction_suppliers = CustomizeFilterConnectionField(AuctionSupplierNode)

    auction_item_supplier = CustomNode.Field(AuctionItemSupplierNode)
    auction_item_suppliers = CustomizeFilterConnectionField(AuctionItemSupplierNode)

    auction_results = relay.ConnectionField(ConectionResults, auction_id=graphene.Int(required=True))

    def resolve_auction_results(root, info, auction_id):
        auction = Auction.objects.get(id=auction_id)
        auction_item = AuctionItem.objects.filter(auction=auction)
        result = []
        has_next_round = Auction.objects.filter(auction_next_round=auction.id).exists()
        for item in auction_item:
            auction_bid = {}
            auction_bid['has_next_round'] = has_next_round
            auction_bid['auction_item_id'] = item.id
            auction_supplier = AuctionSupplier.objects.filter(auction=auction, is_accept=True, supplier_status__in=[6, 8, 9, 10]).order_by('id')
            auction_bid['suppliers'] = []
            for supplier in auction_supplier:
                auction_bids = AuctionBid.objects.filter(user=supplier.user, auction_item=item).order_by('id')
                auction_item_supplier = AuctionItemSupplier.objects.filter(auction_item=item, auction_supplier=supplier).first()
                if auction_bids.exists():
                    price = auction_bids.last().price
                else:
                    price = auction_item_supplier.confirm_price
                auction_bid['suppliers'].append({'user_id': supplier.user.id, 'price': price, 'confirm_price': auction_item_supplier.confirm_price})
            result.append(auction_bid)
        return result

    supplier_awarded_list = graphene.List(UserNode)

    def resolve_supplier_awarded_list(root, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            user = Token.objects.get(key=key).user
            if user.isAdmin():
                list_id = map(
                    lambda x: x.get('user_id'),
                    AuctionSupplier.objects.filter(awarded=1).values('user_id').distinct(),
                )
                return User.objects.filter(id__in=list_id)
            elif user.isBuyer():
                list_id = map(
                    lambda x: x.get('user_id'),
                    AuctionSupplier.objects.filter(awarded=1, auction__user=user).values('user_id').distinct(),
                )
                return User.objects.filter(id__in=list_id)

        except:
            return None
