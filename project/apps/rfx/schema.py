from django.utils import timezone
import django_filters
from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
import graphene
from django_filters import FilterSet, OrderingFilter
from graphql import GraphQLError
from apps.core import CustomNode, CustomizeFilterConnectionField
from apps.users.models import Token, User, Supplier
from apps.rfx.models import (
    RFXData,
    RFXItem,
    RFXAttachment,
    RFXSupplier,
    RFXItemSupplier,
    RFXAward,
)

from apps.users.schema import UserNode, SupplierNode
from django.db.models import Q, Sum, Prefetch
from datetime import timedelta
import math

class GetToken:
    def getToken(info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            return token
        except:
            raise GraphQLError("RFX_01")

class ExtendedConnection(Connection):
    total_count = graphene.Int()

    class Meta:
        abstract = True

    def resolve_total_count(root, info, **kwargs):
        return root.length

class RFXFilter(FilterSet):
    awarded_supplier = django_filters.CharFilter(method="awarded_supplier_filter")
    purchasing_organization = django_filters.CharFilter(field_name="user__buyer__company_full_name", lookup_expr="icontains")
    quote_submited_status = django_filters.CharFilter(field_name="rfx_suppliers__quote_submited_status", lookup_expr="exact")
    general_search = django_filters.CharFilter(method="general_search_filter")
    category = django_filters.CharFilter(field_name="category__id", lookup_expr="exact")
    date_created = django_filters.DateFilter(field_name="created", lookup_expr="date__exact")
    quote_status = django_filters.CharFilter(method="quote_status_filter")
    due_date_from = django_filters.DateFilter(field_name="due_date", lookup_expr="date__gte")
    due_date_to = django_filters.DateFilter(field_name="due_date", lookup_expr="date__lte")
    due_date = django_filters.DateFilter(field_name="due_date", lookup_expr="date__exact")
    class Meta:
        model = RFXData
        fields= {
            'id': ['exact'],
            'item_code': ['icontains'],
            'rfx_type': ['exact'],
            'title': ['icontains'],
            'budget': ['gte', 'lte'],
            'status': ['exact'],   
            'rfx_suppliers__seat_available': ['exact'],              
        }
    order_by = OrderingFilter(
        fields=(
            'id',
            'item_code',
            'rfx_type',
            'title',
            'budget',
            'due_date',
            'status',
            ('supplier_joined_amount', 'amount'),
            ('quote_status', 'quote'),
            ('split_order', 'awarded')
        )
    ) 

    def awarded_supplier_filter(self, queryset, name, value):
        queryset = queryset.filter(rfx_suppliers__user__supplier__company_full_name__icontains=value, rfx_suppliers__quote_submited_status=4)
        return queryset

    def general_search_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(item_code__icontains=value) | Q(title__icontains=value) | Q(rfx_suppliers__user__supplier__company_full_name__icontains=value, rfx_suppliers__quote_submited_status=4)
        ).distinct()
        return queryset

    def quote_status_filter(self, queryset, name, value):
        if int(value) == 1:
            queryset = queryset.filter(is_full=True)
        else:
            queryset = queryset.filter(is_full=False)
        return queryset

def get_rfx_first_round(rfx_data: RFXData):
    if rfx_data.rfx_next_round:
        return get_rfx_first_round(rfx_data.rfx_next_round)
    else:
        return rfx_data

class RFXNode(DjangoObjectType):
    is_next_round = graphene.Boolean()
    awarded_suppliers = graphene.List(SupplierNode)
    sub_amount = graphene.Float()
    best_bid = graphene.Float()
    saving = graphene.Float()
    saving_percentage = graphene.Float()
    rfx_first_round = graphene.Field(lambda: RFXNode)
    class Meta:
        model = RFXData
        filterset_class = RFXFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():                
                queryset = queryset.exclude(status=1).order_by("-id")
            elif user.isSupplier():                    
                queryset = queryset.filter(rfx_suppliers__user=user).exclude(status=1).order_by("-id").prefetch_related(
                    Prefetch(
                        "attachments",
                        queryset = RFXAttachment.objects.filter(attachment_type=2)
                    )
                )
            elif user.isBuyer():
                queryset = queryset.filter(user=user).order_by("-id")
            return queryset
        except:
            raise GraphQLError("RFX_02")

    def resolve_rfx_first_round(self, info):
        if self.rfx_next_round:
            return get_rfx_first_round(self.rfx_next_round)
        else:
            return None

    def resolve_is_next_round(self, info):
        return RFXData.objects.filter(rfx_next_round=self).exists()
    
    def resolve_supplier_joined_amount(self, info):
        return RFXSupplier.objects.filter(rfx=self, is_joined=True).count()

    def resolve_awarded_suppliers(self, info):
        return Supplier.objects.filter(user__user_suppliers__rfx=self, user__user_suppliers__quote_submited_status=4)

    def resolve_sub_amount(self, info):
        try:
            token = GetToken.getToken(info)
            user = token.user
            total = 0
            if self.rfx_next_round is not None:
                rfx_supplier = RFXSupplier.objects.filter(rfx=self.rfx_next_round, user=user).first()
                total = rfx_supplier.sub_total
            return total
        except:
            raise GraphQLError("RFX_02")

    def resolve_best_bid(self, info):
        sub_total = self.rfx_suppliers.filter(is_best_price=True).order_by("sub_total").first().sub_total
        return sub_total

    def resolve_saving(self, info):       
        sub_total = RFXSupplier.objects.filter(rfx=self).order_by("sub_total").first().sub_total
        saving = self.budget - sub_total
        return saving

    def resolve_saving_percentage(self, info):       
        sub_total = RFXSupplier.objects.filter(rfx=self).order_by("sub_total").first().sub_total
        saving = self.budget - sub_total
        percentage = round(saving/self.budget*100, 2)
        return percentage

    def resolve_attachments(self, info):
        return self.attachments.filter(user__isnull=True)

class RFXItemFilter(FilterSet):
    class Meta:
        model = RFXItem
        fields= {
            'id': ['exact'],
            'name': ['icontains'],
            'part_number': ['icontains'],
            'quantity': ['gte', 'lte'],
            'total_amount': ['gte', 'lte'],      
            'unit_price': ['gte', 'lte'],
        }
    order_by = OrderingFilter(
        fields=(
            'id',
            'name',
            'part_number',
            'quantity',
            'total_amount',
            'unit_price'
            )
        ) 

class RFXItemNode(DjangoObjectType):
    class Meta:
        model = RFXItem
        filterset_class = RFXItemFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

class RFXAttachmentFilter(FilterSet):
    internalAttachment = django_filters.CharFilter(method='internal_attachment_filter')
    externalAttachment = django_filters.CharFilter(method='external_attachment_filter')
    class Meta:
        model = RFXAttachment
        fields= {
            'id': ['exact'],
        }
    order_by = OrderingFilter(
        fields=(
            'id',
        )
    ) 

    def internal_attachment_filter(self, queryset, name, value):
        queryset = queryset.filter(rfx_id=value, attachment_type=1)    
        return queryset

    def external_attachment_filter(self, queryset, name, value):
        queryset = queryset.filter(rfx_id=value, attachment_type=2)    
        return queryset

class RFXAttachmentNode(DjangoObjectType):
    class Meta:
        model = RFXAttachment
        filterset_class = RFXAttachmentFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    def resolve_attachment(self, info):
        if self.attachment and hasattr(self.attachment, 'url'):
            return info.context.build_absolute_uri(self.attachment.url)
        else:
            return None

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

class RFXSupplierFilter(FilterSet):
    perchursing_organization = django_filters.CharFilter(field_name="rfx__user__buyer__company_full_name", lookup_expr="icontains")
    due_date = django_filters.DateFilter(field_name="rfx__due_date", lookup_expr="date__exact")
    general_search = django_filters.CharFilter(method="general_search_filter")
    item_supplier_filter = django_filters.BooleanFilter(method="filter_item_supplier")
    category = django_filters.CharFilter(field_name="rfx__category__id", lookup_expr="exact")
    due_date_from = django_filters.DateFilter(field_name="rfx__due_date", lookup_expr="date__gte")
    due_date_to = django_filters.DateFilter(field_name="rfx__due_date", lookup_expr="date__lte")
    class Meta:
        model = RFXSupplier
        fields= {
            'id': ['exact'],
            'rfx__item_code': ['icontains'],
            'rfx__rfx_type': ['exact'],
            'rfx__title': ['icontains'],
            'rfx__budget': ['gte', 'lte'],
            'rfx__status': ['exact'],  
            'quote_submited_status': ['exact'],  
            'seat_available': ['exact'], 
        }
    order_by = OrderingFilter(
        fields=(
            'id',
            ('rfx__item_code', 'item_code'),
            ('rfx__rfx_type', 'type'),
            ('rfx__title', 'title'),
            ('rfx__user__buyer__company_full_name', 'organization'),
            ('rfx__due_date', 'due_date'),
            ('seat_available', 'seat'),
            ('rfx__status', 'status'),
            ('quote_submited_status', 'quote'),
            'sub_total',
        )
    ) 

    def general_search_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(rfx__item_code__icontains=value) | Q(rfx__title__icontains=value) | Q(rfx__user__buyer__company_full_name__icontains=value)
        ).distinct()
        return queryset

    def filter_item_supplier(self, queryset, name, value):
        if value:
            queryset = queryset.exclude(rfx_suppliers__isnull=True)
        return queryset

class RFXSupplierNode(DjangoObjectType):
    attachments = graphene.List(RFXAttachmentNode)

    class Meta:
        model = RFXSupplier
        filterset_class = RFXSupplierFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False
    
    def resolve_attachments(self, info):
        return self.rfx.attachments.filter(user=self.user)

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():                
                queryset = queryset.exclude(rfx__status=1).order_by("-id")
            elif user.isSupplier():
                supplier_instance = user.supplier
                if supplier_instance is None:
                    queryset = queryset.none()
                profile_features = supplier_instance.profile_features
                if profile_features is None:
                    queryset = queryset.none()
                else:
                    rfxr_receiving_priority = profile_features.rfxr_receiving_priority
                    if rfxr_receiving_priority is not None:
                        queryset = queryset.filter(
                            user=user
                        ).exclude(
                            rfx__status=1
                        ).exclude(
                            is_invited=False, rfx__created__gt=timezone.now() - timedelta(hours=rfxr_receiving_priority)
                        ).order_by("-id")
                    else:
                        queryset = queryset.none()
                    
                queryset = queryset.prefetch_related(
                    Prefetch(
                        "rfx__attachments",
                        queryset = RFXAttachment.objects.filter(attachment_type=2)
                    )
                )
            elif user.isBuyer():
                queryset = queryset.filter(rfx__user=user).order_by("-id")
            return queryset.distinct().order_by("-id")
        except Exception as error:
            print(error)
            raise GraphQLError("RFX_02")

class RFXItemSupplierFilter(FilterSet):
    rfx_filter = django_filters.CharFilter(method="filter_rfx")
    class Meta:
        model = RFXItemSupplier
        fields= {
            'id': ['exact'],
            'unit_price': ['gte', 'lte'],  
            'vat_tax': ['gte', 'lte'],      
            'total_amount': ['gte', 'lte'],
        }
    order_by = OrderingFilter(
        fields=(
            'id',
            'unit_price',
            'vat_tax',
            'total_amount',
            )
        ) 

    def filter_rfx(self, queryset, name, value):
        order_instance = queryset.filter(rfx_id=value, rfx_item__rfx_id=value).order_by("-order").first()
        if order_instance is not None:
            order = order_instance.order
            queryset = queryset.filter(rfx_id=value, rfx_item__rfx_id=value, order=order)
        else:
            queryset = queryset.none()
        return queryset

class RFXItemSupplierNode(DjangoObjectType):
    class Meta:
        model = RFXItemSupplier
        filterset_class = RFXItemSupplierFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset    

class RFXAwardFilter(FilterSet):
    class Meta:
        model = RFXAward
        fields= {
            'id': ['exact'],
            'price': ['gte', 'lte'],
            'date': ['gte', 'lte'],      
        }
    order_by = OrderingFilter(
        fields=(
            'id',
            'date',
            'price'
        )
    ) 

class RFXAwardNode(DjangoObjectType):
    class Meta:
        model = RFXAward
        filterset_class = RFXAwardFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

class RFXItemResult(graphene.ObjectType):
    user = graphene.Field(UserNode)
    start_price = graphene.Float()
    end_price = graphene.Float()
    informations = graphene.String()
    proposals = graphene.String()
    percentage = graphene.Float()

    def resolve_user(self, info):
        return User.objects.get(id=self.get('user_id'))


class RFXResults(graphene.ObjectType):
    rfx_item = graphene.Field(RFXItemNode)
    suppliers = graphene.List(RFXItemResult)
    is_next_round = graphene.Boolean()
    
    def resolve_rfx_item(self, info):
        return RFXItem.objects.get(id=self.get('rfx_item_id'))

    def resolve_suppliers(self, info):
        return self.get('suppliers')

    def resolve_has_next_round(self, info):
        return self.get('is_next_round')


class RFXConectionResults(graphene.Connection):
    class Meta:
        node = RFXResults

class RFXAutoItemResult(graphene.ObjectType):   
    submitted_date = graphene.DateTime()
    total_price = graphene.Float()

class RFXAutoResults(graphene.ObjectType):
    user = graphene.Field(UserNode)
    histories = graphene.List(RFXAutoItemResult)

    def resolve_user(self, info):
        return User.objects.get(id=self.get('user_id'))

    def resolve_histories(self, info):
        return self.get('histories')



class RFXAutoConectionResults(graphene.Connection):
    class Meta:
        node = RFXAutoResults
class Query(ObjectType):
    rfx = CustomNode.Field(RFXNode)
    rfxes = CustomizeFilterConnectionField(RFXNode)

    rfx_iterm = CustomNode.Field(RFXItemNode)
    rfx_iterms = CustomizeFilterConnectionField(RFXItemNode)

    rfx_attachment = CustomNode.Field(RFXAttachmentNode)
    rfx_attachments = CustomizeFilterConnectionField(RFXAttachmentNode)

    rfx_supplier = CustomNode.Field(RFXSupplierNode)
    rfx_suppliers = CustomizeFilterConnectionField(RFXSupplierNode)

    rfx_supplier_iterm = CustomNode.Field(RFXItemSupplierNode)
    rfx_supplier_iterms = CustomizeFilterConnectionField(RFXItemSupplierNode)

    rfx_award = CustomNode.Field(RFXAwardNode)
    rfx_awards = CustomizeFilterConnectionField(RFXAwardNode)

    rfx_results = relay.ConnectionField(RFXConectionResults, rfx_id=graphene.Int(required=True))
    def resolve_rfx_results(root, info, rfx_id):
        rfx = RFXData.objects.get(id=rfx_id)
        rfx_items = RFXItem.objects.filter(rfx=rfx)
        result = []
        is_next_round = RFXData.objects.filter(id=rfx.rfx_next_round_id).exists()
        for item in rfx_items:
            rfx_bid = {}
            rfx_bid['is_next_round'] = is_next_round
            rfx_bid['rfx_item_id'] = item.id
            rfx_suppliers = RFXSupplier.objects.filter(rfx=rfx).exclude(sub_total=0).order_by('id')
            rfx_bid['suppliers'] = []
            for supplier in rfx_suppliers:
                percentage = 0
                rfx_award = RFXAward.objects.filter(rfx=rfx, rfx_item=item, user=supplier.user).first()
                if rfx_award is not None:
                    percentage = rfx_award.percentage
                rfx_item_supplier = RFXItemSupplier.objects.filter(rfx_item=item, rfx_supplier__user=supplier.user, rfx=rfx).order_by("-order").first()
                item_supplier = RFXItemSupplier.objects.filter(rfx_item=item, rfx_supplier__user=supplier.user, rfx=rfx).order_by("order").first()
                informations = rfx_item_supplier.informations
                proposals = rfx_item_supplier.proposals
                if is_next_round:
                    is_first_round = True
                    id=rfx.rfx_next_round_id
                    while is_first_round:
                        rfx_data = RFXData.objects.get(id=id)
                        if rfx_data.rfx_type != 3:
                            break
                        if rfx_data is not None and rfx_data.rfx_next_round_id is not None:
                            id=rfx_data.rfx_next_round_id
                        elif rfx_data.rfx_next_round_id is None:                            
                            instance = RFXItemSupplier.objects.filter(rfx_item__part_number=item.part_number, rfx_supplier__user=supplier.user, rfx=rfx_data).order_by("order").first()
                            start_price = instance.total_amount
                            is_first_round = False
                else:
                    start_price = item_supplier.total_amount                
                rfx_bid['suppliers'].append({'user_id': supplier.user.id, 'start_price': start_price, 'end_price': rfx_item_supplier.total_amount, 'informations': informations, 'proposals': proposals, 'percentage': percentage})
            result.append(rfx_bid)
        return result

    rfx_quote_submitted_histories = relay.ConnectionField(RFXAutoConectionResults, rfx_id=graphene.Int(required=True))
    def resolve_rfx_quote_submitted_histories(root, info, rfx_id):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isSupplier():
                result = []
                history = {}
                history['user_id'] = user.id
                history['histories'] = []
                rfx = RFXData.objects.get(id=rfx_id)
                max_order = RFXItemSupplier.objects.filter(rfx_supplier__user=user, rfx=rfx).order_by("-order").first().order
                order = max_order + 1
                for i in range(order):
                    submitted_date = RFXItemSupplier.objects.filter(rfx=rfx, rfx_supplier__user=user, order=i).first().submitted_date
                    total = RFXItemSupplier.objects.filter(rfx=rfx, rfx_supplier__user=user, order=i).aggregate(Sum('total_amount')).get('total_amount__sum')
                    history['histories'].append(
                        {
                            'submitted_date' : submitted_date,
                            'total_price' : total
                        }
                    )
                result.append(history)
                return result
            else:
                raise GraphQLError("RFX_01")
        except:
            raise GraphQLError("RFX_02")