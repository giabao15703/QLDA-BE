import graphene
import graphene_django_optimizer as gql_optimizer
import django_filters

from apps.core import CustomNode, CustomizeFilterConnectionField, Error
from django_filters import FilterSet
from graphene_django import DjangoObjectType
from apps.delivery.models import (
    ShippingFee,
    TransporterList,
    DeliveryResponsible,
    DeTai,
    User,
    GroupQLDA,
    JoinGroup
)
from apps.users.models import Token
from graphene import relay, ObjectType, Connection
from graphql import GraphQLError

class GetToken:
    def getToken(info):
        try:
            key = info.context.headers['Authorization'].split("")
            key = key[-1]
            token = Token.objects.get(key=key)
            return token
        except:
            raise GraphQLError("DELIVERY_01")

class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

class ShippingFeeFilter(FilterSet):
    pick_up_city_code = django_filters.NumberFilter(field_name='pick_up_city_id', lookup_expr="exact")
    pick_up_city_name = django_filters.CharFilter(field_name='pick_up_city__name', lookup_expr="icontains")
    destination_city_code = django_filters.NumberFilter(field_name='destination_city_id', lookup_expr="exact")
    destination_city_name = django_filters.CharFilter(field_name='destination_city__name', lookup_expr="icontains")
    weight = django_filters.NumberFilter(field_name='weight', lookup_expr="exact")
    fee = django_filters.NumberFilter(field_name='fee', lookup_expr="exact")
    status = django_filters.BooleanFilter(field_name='status', lookup_expr="exact")
    class Meta:
        model = ShippingFee
        fields = []

class ShippingFeeNode(DjangoObjectType):
    class Meta:
        model = ShippingFee
        filterset_class = ShippingFeeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class TransporterListFilter(FilterSet):
    short_name = django_filters.CharFilter(field_name="short_name", lookup_expr="icontains")
    long_name = django_filters.CharFilter(field_name="long_name", lookup_expr="icontains")
    code = django_filters.CharFilter(field_name='code', lookup_expr="exact")
    tax = django_filters.CharFilter(field_name='tax', lookup_expr="exact")
    phone = django_filters.CharFilter(field_name='phone', lookup_expr="exact")
    address = django_filters.CharFilter(field_name='address', lookup_expr="icontains")
    email = django_filters.CharFilter(field_name='email', lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name='status', lookup_expr="exact")

    class Meta:
        model = TransporterList
        fields = []

class TransporterListNode(DjangoObjectType):
    class Meta:
        model = TransporterList
        filterset_class = TransporterListFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class DeliveryResponsibleFilter(FilterSet):
    transporter_code = django_filters.CharFilter(field_name="transporter_code_id", lookup_expr="exact")
    transporter_short_name = django_filters.CharFilter(field_name="transporter_code__short_name", lookup_expr="icontains")
    city_code = django_filters.CharFilter(field_name='city_code_id', lookup_expr="exact")
    city_name = django_filters.CharFilter(field_name='city_code__name', lookup_expr="icontains")

    class Meta:
        model = DeliveryResponsible
        fields = []

class DeliveryResponsibleNode(DjangoObjectType):
    class Meta:
        model = DeliveryResponsible
        filterset_class = DeliveryResponsibleFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class DeTaiFilter(FilterSet):
    id = django_filters.CharFilter(field_name='id', lookup_expr="exact")
    giang_vien = django_filters.CharFilter(field_name='giang_vien__full_name', lookup_expr="icontains")
    ten_de_tai = django_filters.CharFilter(field_name='ten_de_tai', lookup_expr="icontains")
    mo_ta = django_filters.CharFilter(field_name='mo_ta', lookup_expr="icontains")

    class Meta:
        model = DeTai
        fields = []


class DeTaiNode(DjangoObjectType):
    giang_vien_full_name = graphene.String()

    class Meta:
        model = DeTai
        filterset_class = DeTaiFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_giang_vien_full_name(self, info):
        return self.giang_vien.full_name 



class GroupQLDAFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name="status")

    def filter_members_count(self, queryset, name, value):
        return queryset.annotate(num_members=models.Count('members')).filter(num_members=value)

    class Meta:
        model = GroupQLDA
        fields = []


class GroupQLDANode(DjangoObjectType):
    members_count = graphene.Int()

    class Meta:
        model = GroupQLDA
        filterset_class = GroupQLDAFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class JoinGroupNode(DjangoObjectType):
    members_count = graphene.Int()

    class Meta:
        model = JoinGroup
        filterset_class = GroupQLDAFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class Query(object):
    shipping_fee = CustomNode.Field(ShippingFeeNode)
    shipping_fees = CustomizeFilterConnectionField(ShippingFeeNode)
    
    transporter_list = CustomNode.Field(TransporterListNode)
    transporter_lists = CustomizeFilterConnectionField(TransporterListNode)

    delivery_responsible = CustomNode.Field(DeliveryResponsibleNode)
    delivery_responsibles = CustomizeFilterConnectionField(DeliveryResponsibleNode)

    de_tai = CustomNode.Field(DeTaiNode)
    de_tais = CustomizeFilterConnectionField(DeTaiNode)

    group_qlda = CustomNode.Field(GroupQLDANode)
    group_qldas = CustomizeFilterConnectionField(GroupQLDANode, filterset_class=GroupQLDAFilter)

    join_group = CustomNode.Field(JoinGroupNode)

