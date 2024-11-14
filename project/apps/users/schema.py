import random
import graphene
import django_filters
import graphene_django_optimizer as gql_optimizer

from apps.auctions.models import Auction
from apps.core import CustomNode, CustomizeFilterConnectionField, Error
from apps.graphene_django_plus.mutations import ModelUpdateMutation
from apps.master_data.models import (
    Promotion,
    EmailTemplates,
    FamilyCode,
    ClusterCode,
    SubClusterCode,
    Category
)
from apps.master_data.schema import LanguageNode, CategoryNode, SubClusterCodeNode
from apps.users.models import (
    Supplier,
    SupplierFlashSale,
    User,
    Buyer,
    BuyerSubAccounts,
    BuyerSubAccountsActivity,
    SupplierPortfolio,
    BuyerIndustry,
    Admin,
    UsersPermission,
    GroupPermission,
    UserSubstitutionPermission,
    BuyerActivity,
    SupplierIndustry,
    SupplierClientFocus,
    SupplierCategory,
    SupplierActivity,
    SupplierCompanyCredential,
    SupplierBusinessLicense,
    SupplierFormRegistrations,
    SupplierQualityCertification,
    SupplierTaxCertification,
    SupplierOthers,
    SupplierBankCertification,
    SupplierSubAccount,
    SupplierSubAccountActivity,
    UserDiamondSponsor,
    Token,
    SupplierSICP,
    SupplierSICPFile,
    SICPTextEditor,
    SICPTextEditorFile,
    UserDiamondSponsorFee,
    SupplierProduct,
    ProductConfirmStatus,
    SupplierProductImage,
    SupplierProductFlashSale,
    SupplierProductWholesalePrice,
    ProductType,
    SupplierCertificate,
    SupplierProductCategory,
    UserFollowingSupplier,
    UserFollowingSupplierStatus,
    UserRatingSupplierProduct,
)
from apps.users.error_code import UserError
from apps.payment.models import UserPayment
from apps.sale_schema.models import ProfileFeaturesSupplier, SICPRegistration

from datetime import datetime
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from django.db.models import BooleanField, ExpressionWrapper, F, Prefetch, Q, Count, Exists, OuterRef
from django.template import Template, Context
from django_filters import FilterSet, OrderingFilter

from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

class GetToken:
    def getToken(info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            return token
        except:
            raise GraphQLError("USER_12")

class UserInterface(graphene.Interface):
    email = graphene.String()
    short_name = graphene.String()
    full_name = graphene.String()
    username = graphene.String()
    user_type = graphene.Int()
    created = graphene.DateTime()
    first_name = graphene.String()
    last_name = graphene.String()
    company_website = graphene.String()
    company_long_name = graphene.String()
    company_short_name = graphene.String()

    @classmethod
    def resolve_type(cls, instance, info):
        user = User.objects.get(id=instance.user_id)
        if user.user_type == 1:
            return AdminNode
        if user.user_type == 2 and user.company_position == 1:
            return BuyerNode
        if user.user_type == 3 and user.company_position == 1:
            return SupplierNode
        if user.user_type == 2 and user.company_position == 2:
            return BuyerSubAccountsNode
        if user.user_type == 3 and user.company_position == 2:
            return SupplierSubAccountNode

    def resolve_username(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.username

    def resolve_email(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.email

    def resolve_short_name(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.short_name

    def resolve_full_name(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.full_name

    def resolve_created(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.created

    def resolve_first_name(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.first_name

    def resolve_last_name(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.last_name

    def resolve_user_type(cls, info):
        user = User.objects.get(id=cls.user_id)
        return user.user_type


class BuyerFilter(FilterSet):
    created = django_filters.CharFilter(method='created_filter')
    username = django_filters.CharFilter(method='username_filter')
    username_exact = django_filters.CharFilter(method='username_exact_filter')
    email = django_filters.CharFilter(method='email_filter')
    status = django_filters.CharFilter(method='status_filter')
    valid_from = django_filters.CharFilter(method='valid_from_filter')
    valid_to = django_filters.CharFilter(method='valid_to_filter')
    profile_feature = django_filters.CharFilter(method='profile_feature_filter')
    auctions_year = django_filters.CharFilter(method='auctions_year_filter')
    rfx_cancel = django_filters.CharFilter(method='rfx_cancel_filter')
    changed_by = django_filters.CharFilter(method='changed_by_filter')
    changed_date = django_filters.CharFilter(method='changed_date_filter')
    reason_manual = django_filters.CharFilter(method='reason_manual_filter')
    full_name = django_filters.CharFilter(method='full_name_filter')
    changed_state = django_filters.CharFilter(method='changed_state_filter')

    class Meta:
        model = Buyer
        fields = ['id']

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('user__email', 'email'),
            ('user__created', 'created'),
            ('user__status', 'status'),
            ('user__username', 'username'),
            ('user__full_name', 'full_name'),
            ('profile_features__name', 'profile_features'),
            ('profile_features__no_eauction_year', 'auctions_year'),
            ('profile_features__rfx_year', 'rfx_cancel'),
            ('valid_from', 'valid_from'),
            ('valid_to', 'valid_to'),
        )
    )

    def email_filter(self, queryset, name, value):
        queryset = queryset.filter(user__email__icontains=value)
        return queryset

    def username_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username__icontains=value)
        return queryset

    def username_exact_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username__exact=value)
        return queryset

    def status_filter(self, queryset, name, value):
        queryset = queryset.filter(user__status=value)
        return queryset

    def created_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(user__created__range=(value, value_to))
        return queryset

    def full_name_filter(self, queryset, name, value):
        queryset = queryset.filter(user__full_name__contains=value)
        return queryset

    def valid_from_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(valid_from__gte=value)
        return queryset

    def valid_to_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(valid_to__lte=value)
        return queryset

    def profile_feature_filter(self, queryset, name, value):
        queryset = queryset.filter(profile_features_id=value)
        return queryset

    def auctions_year_filter(self, queryset, name, value):
        queryset = queryset.filter(profile_features__no_eauction_year=value)
        return queryset

    def rfx_cancel_filter(self, queryset, name, value):
        queryset = queryset.filter(profile_features__rfx_year=value)
        return queryset

    def changed_by_filter(self, queryset, name, value):
        list_system = []
        list_user_id = map(lambda x: x.get('id'), User.objects.filter(username__icontains=value).values('id'))
        list_id = map(lambda x: x.get('buyer_id'), BuyerActivity.objects.filter(changed_by_id__in=list_user_id).values('buyer_id'))
        if value in "system":
            list_system = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(changed_by_id=None).values('supplier_id'))
        list_id = list(list_id) + list(list_system)
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        list_id = map(lambda x: x.get('buyer_id'), BuyerActivity.objects.filter(changed_date__range=(value, value_to)).values('buyer_id'))
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def reason_manual_filter(self, queryset, name, value):
        list_id = map(lambda x: x.get('buyer_id'), BuyerActivity.objects.filter(reason_manual__icontains=value).values('buyer_id'))
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_state_filter(self, queryset, name, value):
        list_id = map(lambda x: x.get('buyer_id'), BuyerActivity.objects.filter(changed_state=value).values('buyer_id'))
        queryset = queryset.filter(id__in=list_id)
        return queryset


class BuyerActivityFilter(FilterSet):
    changed_by = django_filters.CharFilter(method='changed_by_filter')
    changed_date = django_filters.CharFilter(method='changed_date_filter')
    reason_manual = django_filters.CharFilter(method='reason_manual_filter')
    changed_state = django_filters.CharFilter(method='changed_state_filter')

    class Meta:
        model = Buyer
        fields = ['id']

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('changed_by__short_name', 'changed_by'),
            ('changed_date', 'changed_date'),
            ('reason_manual', 'reason_manual'),
            ('changed_state', 'changed_state'),
        )
    )

    def changed_by_filter(self, queryset, name, value):
        queryset = queryset.filter(changed_by__username__icontains=value)
        return queryset

    def changed_date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(changed_date__range=(value, value_to))
        return queryset

    def reason_manual_filter(self, queryset, name, value):
        queryset = queryset.filter(reason_manual__icontains=value)
        return queryset

    def changed_state_filter(self, queryset, name, value):
        queryset = queryset.filter(changed_state=value)
        return queryset

class SupplierFilter(FilterSet):
    rating_star = django_filters.CharFilter(method='rating_star_filter')
    company_country = django_filters.CharFilter(method='company_country_filter')
    company_country_state = django_filters.CharFilter(method='company_country_state_filter')
    company_number_of_employee = django_filters.CharFilter(method='number_of_employee')
    company_full_name = django_filters.CharFilter(lookup_expr='contains')
    project_size = django_filters.CharFilter(method='project_size_filter')
    email = django_filters.CharFilter(method='email_filter')
    username = django_filters.CharFilter(method='username_filter')
    username_exact = django_filters.CharFilter(method='username_exact_filter')
    status = django_filters.CharFilter(method='status_filter')
    created = django_filters.CharFilter(method='created_filter')
    valid_from = django_filters.CharFilter(method='valid_from_filter')
    valid_to = django_filters.CharFilter(method='valid_to_filter')
    profile_feature = django_filters.CharFilter(method='profile_feature_filter')
    report_year = django_filters.CharFilter(method='report_year_filter')
    flash_sale = django_filters.CharFilter(method='flash_sale_filter')
    changed_by = django_filters.CharFilter(method='changed_by_filter')
    changed_date = django_filters.CharFilter(method='changed_date_filter')
    reason_manual = django_filters.CharFilter(method='reason_manual_filter')
    changed_state = django_filters.CharFilter(method='changed_state_filter')
    company_city = django_filters.CharFilter(lookup_expr='icontains')

    locations = django_filters.CharFilter(field_name="company_country__id", lookup_expr="exact")
    id = django_filters.CharFilter(field_name="id", lookup_expr="exact")

    pro_size_filter = django_filters.CharFilter(method='filter_pro_size')
    client_focus_filter = django_filters.CharFilter(method='filter_client_focus')
    employee_filter = django_filters.CharFilter(method='filter_employee')
    company_name_filter = django_filters.CharFilter(method='filter_company_name')
    industry_focus_filter = django_filters.CharFilter(method='filter_industry_focus')
    industry_cluster_filter = django_filters.CharFilter(method='filter_industry_cluster')
    cluster_filter = django_filters.CharFilter(method="filter_cluster")
    
    family_filter = django_filters.CharFilter(method="filter_family")
    supplier_flash_sale_filter = django_filters.BooleanFilter(method="filter_flash_sale_supplier")
    sub_cluster_filter = django_filters.CharFilter(method="filter_subcluster_code")
    discription_filter = django_filters.CharFilter(method="filter_category")
    minimum_order_value_from = django_filters.CharFilter(field_name="suppliercategory__minimum_of_value", lookup_expr="gte")
    minimum_order_value_to = django_filters.CharFilter(field_name="suppliercategory__minimum_of_value", lookup_expr="lte")
    minimum_order_value = django_filters.CharFilter(field_name="suppliercategory__minimum_of_value", lookup_expr="exact")

    category = django_filters.CharFilter(method='category_filter')

    class Meta:
        model = Supplier
        fields= {
            'id': ['exact'],
        }
    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('user__email', 'email'),
            ('user__created', 'created'),
            ('user__status', 'status'),
            ('user__username', 'username'),
            ('profile_features__name', 'profile_features'),
            ('profile_features__report_year', 'report_year'),
            ('profile_features__flash_sale', 'flash_sale'),
            ('valid_from', 'valid_from'),
            ('valid_to', 'valid_to'),
            ('company_full_name', 'company_name'),
            ('profile_features__name', 'sponsor'),
            'employees',
            'viewed',
            ('profile_features__profile_features_type', 'order'),
            ('sicp_registration__sicp_type', 'sicp')
        )
    ) 
    def filter_subcluster_code(self, queryset, name, value):
        queryset = queryset.filter(suppliercategory__category_id__sub_cluster_code_id__id=value)
        return queryset.distinct().order_by("-profile_features__name")

    def filter_category(self, queryset, name, value):
        queryset = queryset.filter(suppliercategory__category_id__id=value)
        return queryset.distinct().order_by("-profile_features__name")

    def filter_flash_sale_supplier(self, queryset, name, value):
        if value == False:
            queryset = queryset.filter(supplierflashsale__is_active=True, supplierflashsale__is_confirmed=1)
        return queryset.distinct().order_by("id")

    def filter_cluster(self, queryset, name, value):
        queryset = queryset.filter(suppliercategory__category_id__sub_cluster_code_id__cluster_code_id__id=value)
        return queryset.distinct().order_by("-profile_features__name")

    def filter_family(self, queryset, name, value):
        queryset = queryset.filter(suppliercategory__category_id__sub_cluster_code_id__cluster_code_id__family_code_id__id=value)
        return queryset.distinct().order_by("-profile_features__name")

    def filter_industry_cluster(self, queryset, name, value):
        queryset = queryset.filter(supplierindustry__industry_sub_sectors__industry_sectors__industry_cluster__id=value)
        return queryset.distinct().order_by("id")

    def filter_industry_focus(self, queryset, name, value):
        queryset = queryset.filter(supplierindustry__industry_sub_sectors__industry_sectors__industry_cluster__industry__id=value)
        return queryset.distinct().order_by("id")
    
    def filter_pro_size(self, queryset, name, value):
        value = value.split(",")
        data0 = {}
        data1 = {"suppliercategory__minimum_of_value__lt": 1000}
        data2 = {"suppliercategory__minimum_of_value__lt": 2000, "suppliercategory__minimum_of_value__gte": 1000}
        data3 = {"suppliercategory__minimum_of_value__lt": 5000, "suppliercategory__minimum_of_value__gte": 2000}
        data4 = {"suppliercategory__minimum_of_value__lt": 10000, "suppliercategory__minimum_of_value__gte": 5000}
        data5 = {"suppliercategory__minimum_of_value__lt": 25000, "suppliercategory__minimum_of_value__gte": 10000}
        data6 = {"suppliercategory__minimum_of_value__lt": 50000, "suppliercategory__minimum_of_value__gte": 25000}
        data7 = {"suppliercategory__minimum_of_value__lt": 100000, "suppliercategory__minimum_of_value__gte": 50000}
        data8 = {"suppliercategory__minimum_of_value__gte": 100000}
        data = [data0, data1, data2, data3, data4, data5, data6, data7, data8]

        query = queryset.filter(**data[int(value[0])])
        for i in range(1, len(value)):
            temp = int(value[i])
            query = query | queryset.filter(**data[temp])
        return query.distinct().order_by("id")

    def filter_client_focus(self, queryset, name, value):
        value = value.split(",")
        data0 = {}
        data1 = {"supplierclientfocus__client_focus__id": 1}
        data2 = {"supplierclientfocus__client_focus__id": 2}
        data3 = {"supplierclientfocus__client_focus__id": 3}
        data = [data0, data1, data2, data3]

        query = queryset.filter(**data[int(value[0])])
        for i in range(1, len(value)):
            temp = int(value[i])
            query = query | queryset.filter(**data[temp])
        return query.distinct().order_by("id")

    def filter_employee(self, queryset, name, value):
        value = value.split(",")
        data0 = {}
        data1 = {"company_number_of_employee__id": 1}
        data2 = {"company_number_of_employee__id": 2}
        data3 = {"company_number_of_employee__id": 3}
        data4 = {"company_number_of_employee__id": 4}
        data5 = {"company_number_of_employee__id": 5}
        data6 = {"company_number_of_employee__id": 6}
        data7 = {"company_number_of_employee__id": 7}
        data = [data0, data1, data2, data3, data4, data5, data6, data7]

        query = queryset.filter(**data[int(value[0])])
        for i in range(1, len(value)):
            temp = int(value[i])
            query = query | queryset.filter(**data[temp])
        return query.distinct().order_by("id")

    def filter_company_name(self, queryset, name, value):
        value = value.split(",")
        query = queryset.filter(company_full_name__icontains=value[0])
        for i in range(1, len(value)):
            temp = value[i]
            query = query | queryset.filter(company_full_name__icontains=temp)
        return query.distinct().order_by("id")

    def company_country_filter(self, queryset, name, value):
        queryset = queryset.filter(company_country__id__exact=value)
        return queryset

    def company_country_state_filter(self, queryset, name, value):
        queryset = queryset.filter(company_country_state__id__exact=value)
        return queryset

    def rating_star_filter(self, queryset, name, value):
        number_input = value.strip().split(',')
        queryset = queryset.filter(rating_star_id__in=number_input)
        return queryset

    def number_of_employee(self, queryset, name, value):
        number_input = value.strip().split(',')
        queryset = queryset.filter(company_number_of_employee__in=number_input)
        return queryset

    def project_size_filter(self, queryset, name, value):
        number_input = value.strip().split(',')
        queryset = queryset.filter(project_size_id__in=number_input)
        return queryset

    def rating_star_filter(self, queryset, name, value):
        number_input = value.strip().split(',')
        queryset = queryset.filter(rating_star_id__in=number_input)
        return queryset

    def email_filter(self, queryset, name, value):
        queryset = queryset.filter(user__email__icontains=value)
        return queryset

    def username_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username__icontains=value)
        return queryset

    def username_exact_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username__exact=value)
        return queryset

    def status_filter(self, queryset, name, value):
        queryset = queryset.filter(user__status=value)
        return queryset

    def created_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(user__created__range=(value, value_to))
        return queryset

    def valid_from_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(valid_from__gte=value)
        return queryset

    def valid_to_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(valid_to__lte=value)
        return queryset

    def profile_feature_filter(self, queryset, name, value):
        queryset = queryset.filter(profile_features_id=value)
        return queryset

    def report_year_filter(self, queryset, name, value):
        queryset = queryset.filter(profile_features__report_year=value)
        return queryset

    def flash_sale_filter(self, queryset, name, value):
        queryset = queryset.filter(profile_features__flash_sale=value)
        return queryset

    def changed_by_filter(self, queryset, name, value):
        list_system = []
        list_user_id = map(lambda x: x.get('id'), User.objects.filter(username__icontains=value).values('id'))
        list_id = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(changed_by_id__in=list_user_id).values('supplier_id'))
        if value in "system":
            list_system = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(changed_by_id=None).values('supplier_id'))
        list_id = list(list_id) + list(list_system)
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        list_id = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(changed_date__range=(value, value_to)).values('supplier_id'))
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def reason_manual_filter(self, queryset, name, value):
        list_id = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(reason_manual__icontains=value).values('supplier_id'))
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_state_filter(self, queryset, name, value):
        list_id = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(changed_state=value).values('supplier_id'))
        queryset = queryset.filter(id__in=list_id)
        return queryset
    
    def category_filter(self, queryset, name, value):
        queryset = queryset.filter(Exists(SupplierCategory.objects.filter(user_supplier=OuterRef('pk'), category__id__exact=value)))
        return queryset


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length


class UserNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = User
        filter_fields = ['id']
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset

class SupplierFlashSaleFilter(FilterSet):
    user_supplier = django_filters.CharFilter(field_name="user_supplier__id", lookup_expr="exact")
    company_name = django_filters.CharFilter(field_name="user_supplier__company_full_name", lookup_expr="icontains")
    is_discounted_price_sorted = django_filters.BooleanFilter(method="sort", lookup_expr="exact")
    is_active =  django_filters.BooleanFilter(field_name="is_active", lookup_expr="exact")
    is_confirmed = django_filters.NumberFilter(field_name="is_confirmed", lookup_expr="exact")
    discounted_price_from = django_filters.NumberFilter(method="discounted_price_from_value")
    discounted_price_to = django_filters.NumberFilter(method="discounted_price_to_value")
    company_name_filter = django_filters.CharFilter(method='filter_company_name')
    flag = django_filters.BooleanFilter(method="flag_filter")
    is_display = django_filters.BooleanFilter(method="is_display_filter")
    exclude_id_list = django_filters.CharFilter(method="exclude_is_in_list")

    class Meta:
        model = SupplierFlashSale
        fields= {
            'id': ['exact'],
            'sku_number': ['icontains'],
            'initial_price': ['gte', 'lte'],
            'description': ['icontains'],
            'user_supplier': ['exact'],
        }
    order_by = OrderingFilter(fields=('id','sku_number','initial_price','description','user_supplier','is_active','is_confirmed')) 

    def is_display_filter(self, queryset, name, value):
        if value == False:
            queryset = queryset.filter(is_active=True, is_confirmed=1).order_by("id")
        return queryset

    def flag_filter(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():                
                queryset = queryset.all().order_by("id")
            elif user.isSupplier():
                if value == True:
                    queryset = queryset.filter(user_supplier_id__user_id=user.id).order_by("re_order")
                else:
                    queryset = queryset.filter(is_active=True, is_confirmed=1).order_by("id")
            return queryset
        except:
            return queryset.filter(is_active=True, is_confirmed=1).order_by("id")

    def sort(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(final_price=(F('initial_price') - (F('initial_price') * F('percentage'))/100)).order_by('final_price')
        else:
            queryset = queryset.annotate(final_price=(F('initial_price') - (F('initial_price') * F('percentage'))/100)).order_by('-final_price')
        return queryset
    
    def discounted_price_from_value(self, queryset, name, value):
        queryset = queryset.annotate(final_price=(F('initial_price') - (F('initial_price') * F('percentage'))/100)).filter(final_price__gte=value)
        return queryset

    def discounted_price_to_value(self, queryset, name, value):
        queryset = queryset.annotate(final_price=(F('initial_price') - (F('initial_price') * F('percentage'))/100)).filter(final_price__lte=value)
        return queryset

    def filter_company_name(self, queryset, name, value):
        value_list = value.split(",")
        if len(value_list) > 0:
            query = Q()
            for v in value_list:
                query.add(Q(user_supplier__company_full_name__icontains=v),Q.OR)
            queryset = queryset.filter(query)
        return queryset.distinct().order_by("id")

    def exclude_is_in_list(self, queryset, name, value):
        if value is not None and value != "":
            queryset = queryset.exclude(id__in=[s for s in value.split(",") if s.isdigit()])
        return queryset

class SupplierProductFilter(FilterSet):
    user_supplier = django_filters.CharFilter(field_name="user_supplier_id", lookup_expr="exact")
    type =  django_filters.CharFilter(field_name="type", lookup_expr="exact")
    is_visibility = django_filters.BooleanFilter(field_name="is_visibility", lookup_expr="exact")
    discounted_price_from = django_filters.NumberFilter(field_name="product_flash_sales__discounted_price", lookup_expr="gte", distinct=True)
    discounted_price_to = django_filters.NumberFilter(field_name="product_flash_sales__discounted_price", lookup_expr="lte", distinct=True)
    is_display = django_filters.BooleanFilter(method="is_display_filter")
    exclude_id_list = django_filters.CharFilter(method="exclude_is_in_list")
    initial_price_from = django_filters.NumberFilter(field_name="product_flash_sales__initial_price", lookup_expr="gte", distinct=True)
    initial_price_to = django_filters.NumberFilter(field_name="product_flash_sales__initial_price", lookup_expr="lte", distinct=True)
    confirmed_status = django_filters.ChoiceFilter(field_name="confirmed_status", lookup_expr="exact", choices=ProductConfirmStatus.choices)
    type = django_filters.ChoiceFilter(field_name="type", lookup_expr="exact", choices=ProductType.choices)
    company_name_filter = django_filters.CharFilter(method='filter_company_name')
    supplier_no = django_filters.CharFilter(method='filter_supplier_no')

    class Meta:
        model = SupplierProduct
        fields= {
            'id': ['exact'],
            'sku_number': ['icontains'],
            'description': ['icontains'],
            'user_supplier': ['exact'],
            "is_visibility": ["exact"],
            'product_name': ['icontains'],
        }
    order_by = OrderingFilter(fields=('id','sku_number','initial_price','description','user_supplier','is_active','is_confirmed')) 

    def is_display_filter(self, queryset, name, value):
        if value == False:
            queryset = queryset.filter(is_active=True, is_confirmed=1).order_by("id")
        return queryset

    def filter_company_name(self, queryset, name, value):
        value_list = value.split(",")
        if len(value_list) > 0:
            query = Q()
            for v in value_list:
                query.add(Q(user_supplier__company_full_name__icontains=v),Q.OR)
            queryset = queryset.filter(query)
        return queryset.distinct().order_by("id")

    def filter_supplier_no(self, queryset, name, value):
        value_list = value.split(",")
        if len(value_list) > 0:
            queryset = queryset.filter(user_supplier__user__username=value)
        return queryset.distinct().order_by("id")

    def exclude_is_in_list(self, queryset, name, value):
        if value is not None and value != "":
            queryset = queryset.exclude(id__in=[s for s in value.split(",") if s.isdigit()])
        return queryset

class SupplierFlashSaleConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    reach = graphene.Boolean()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_reach(root, info, **kwargs):
        key = info.context.headers.get('Authorization')
        user = None
        if key is not None:
            key = key.split(" ")[-1]
            token = Token.objects.filter(key=key).first()
            if token is not None:
                user = token.user

        for supplierNode in root.edges:
            supplier_flash_sale = supplierNode.node
            if user and user.isSupplier():
                if user.supplier_sub_account.exists():
                    if user.supplier_sub_account.first().supplier == supplier_flash_sale.user_supplier:
                        continue
                else:
                    if user.supplier == supplier_flash_sale.user_supplier:
                        continue
            supplierNode.node.reach_number = supplierNode.node.reach_number + 1
            supplierNode.node.save()
        return True

class SupplierFlashSaleNode(DjangoObjectType):
    discounted_price = graphene.Float()
    is_confirmed = graphene.Int()

    class Meta:
        model = SupplierFlashSale
        filterset_class = SupplierFlashSaleFilter
        interfaces = (CustomNode,)
        connection_class = SupplierFlashSaleConnection

    def resolve_picture(self, info):
        return info.context.build_absolute_uri(self.picture.url)

    def resolve_discounted_price(self, info):
        percent = self.percentage
        initial_price = self.initial_price
        discounted_price = initial_price - (initial_price * percent) / 100
        return discounted_price
    
    def resolve_is_confirmed(self, info):
        return self.is_confirmed

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():                
                queryset = queryset.all().order_by("id")
            return queryset
        except:
            return gql_optimizer.query(queryset.filter(is_active=True, is_confirmed=1).order_by("id"), info)

class SupplierProductConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    reach = graphene.Boolean()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_reach(root, info, **kwargs):
        try:
            key = info.context.headers.get('Authorization')
            user = None
            if key is not None:
                key = key.split(" ")[-1]
                token = Token.objects.filter(key=key).first()
                if token is not None:
                    user = token.user
            is_supplier = bool(user and user.isSupplier())
            if is_supplier:
                if user.supplier_sub_account.exists():
                    checked_supplier = user.supplier_sub_account.first().supplier
                else:
                    checked_supplier = user.supplier
            for supplierNode in root.edges:
                supplier_product = supplierNode.node
                if is_supplier:
                    if checked_supplier == supplier_product.user_supplier:
                        continue
                supplierNode.node.reach_number = supplierNode.node.reach_number + 1
                supplierNode.node.save()
            return True
        except:
            return False

class SupplierProductImageNode(DjangoObjectType):
    class Meta:
        model = SupplierProductImage
        fields = ["id", "image"]

    def resolve_image(self, info):
        if self.image and hasattr(self.image, "url"):
            return info.context.build_absolute_uri(self.image.url)
        else:
            return None

class SupplierProductFlashSaleNode(DjangoObjectType):
    class Meta:
        model = SupplierProductFlashSale
        fields = ["id", "initial_price", "discounted_price"]

class SupplierProductWholesalePriceNode(DjangoObjectType):
    class Meta:
        model = SupplierProductWholesalePrice
        fields = ["id", "quality_from", "quality_to", "price_bracket", "delivery_days"]

class SpecificationsType(graphene.ObjectType):
    color = graphene.String()
    size = graphene.String()
    weight = graphene.String()
    height = graphene.String()
    images = graphene.List(graphene.String)

class GeneralInformationType(graphene.ObjectType):
    product_service_type = graphene.String()
    product_service_name = graphene.String()
    unit = graphene.String()
    minimum_order_quantity = graphene.Int()
    sku_number = graphene.String()
    currency = graphene.String()
    product_service_description = graphene.String()
    product_specification = graphene.String()

class ProductGroupType(graphene.ObjectType):
    regular_product = graphene.Boolean()
    green_product = graphene.Boolean()
    official_product = graphene.Boolean()
    

class ProductPriceType(graphene.ObjectType):
    initial_price = graphene.Float()
    reduced_price = graphene.Float()

class ProductInfoType(graphene.ObjectType):
    product_images = graphene.List(graphene.String)

class WholeSalePriceType(graphene.ObjectType):
    quality_from = graphene.Int()
    quality_to = graphene.Int()
    price_bracket = graphene.String()
    delivery_days = graphene.Int()

class ProductServiceDetailType(graphene.ObjectType):
    product_status = graphene.String()
    brand = graphene.String()
    origin = graphene.String()
    country = graphene.String()
    guarantee = graphene.String()
    state = graphene.String()
    status = graphene.String()

class SupplierProductNode(DjangoObjectType):
    picture = graphene.String()
    initial_price = graphene.Float()
    discounted_price = graphene.Float()
    category_list = graphene.List(CategoryNode)
    related_supplier_product_list = graphene.List(lambda: SupplierProductNode)

    product_service_description = graphene.String()
    specifications = graphene.Field(SpecificationsType)
    general_information_type = graphene.Field(GeneralInformationType)
    product_group = graphene.Field(ProductGroupType)
    product_price = graphene.Field(ProductPriceType)
    product_info = graphene.Field(ProductInfoType)
    whole_sale_price = graphene.List(WholeSalePriceType)
    product_service_detail = graphene.Field(ProductServiceDetailType)

    class Meta:
        model = SupplierProduct
        filterset_class = SupplierProductFilter
        interfaces = (CustomNode,)
        connection_class = SupplierProductConnection

    def resolve_product_service_detail(self, info):
        return ProductServiceDetailType(
            product_status=self.confirmed_status,
            brand=self.brand,
            origin=self.origin_of_production,
            country=self.country.name,
            guarantee=self.guarantee,
            state=self.state.name,
            status=self.status
        )

    def resolve_whole_sale_price(self, info):
        return self.product_wholesale_price_list.all()   

    def resolve_product_info(self, info):
        return ProductInfoType(
            product_images=self.product_images.all().values_list('image', flat=True)
        )

    def resolve_product_price(self, info):
        if self.product_flash_sales.exists():
            return ProductPriceType(
                initial_price=self.product_flash_sales.first().initial_price,
                reduced_price=self.product_flash_sales.first().discounted_price
            )
        return None

    def resolve_product_group(self, info):
        return ProductGroupType(
            regular_product=self.regular_product,
            green_product=self.green_product,
            official_product=self.official_product
        )

    def resolve_general_information_type(self, info):
        return GeneralInformationType(
            product_service_type=self.type,
            product_service_name=self.product_name,
            unit=self.unit_of_measure.name,
            minimum_order_quantity=self.minimum_order_quantity,
            sku_number=self.sku_number,
            currency=self.currency.name,
            product_service_description=self.description,
            product_specification=self.specification
        )

    def resolve_specifications(self, info):
        return SpecificationsType(
            color=self.color,
            size=self.size,
            weight=self.weight,
            height=self.height,
            images=self.product_images.all().values_list('image', flat=True)
        )

    def resolve_product_service_description(self, info, **kwargs):
        if self.description:
            return self.description
        return None

    def resolve_picture(self, info, **kwargs):
        if self.product_images.exists():
            picture = self.product_images.all().order_by("id").first().image
            if picture and hasattr(picture, 'url'):
                if picture.url.lower().replace('/media/', '').startswith("http"):
                    return picture
                return info.context.build_absolute_uri(picture.url)
        return None

    def resolve_initial_price(self, info, **kwargs):
        if self.product_flash_sales.exists():
            return self.product_flash_sales.first().initial_price
        return None

    def resolve_discounted_price(self, info, **kwargs):
        if self.product_flash_sales.exists():
            return self.product_flash_sales.first().discounted_price
        return None

    def resolve_category_list(self, info, **kwargs):
        if self.supplier_product_category_list.exists():
            return [x.category for x in self.supplier_product_category_list.all()]
        return []

    def resolve_related_supplier_product_list(self, info, **kwargs):
        return [x.related_supplier_product for x in self.related_supplier_product_product.all()]
    
    def resolve_product_flash_sales(self, info, **kwargs):
        if hasattr(self, 'product_flash_sales'):
            return self.product_flash_sales
        return self.product_flash_sales.all()
    
    def resolve_product_wholesale_price_list(self, info, **kwargs):
        if hasattr(self, 'product_wholesale_price_list'):
            return self.product_wholesale_price_list
        return self.product_wholesale_price_list.all()

    @classmethod
    def get_queryset(cls, queryset, info):
        return gql_optimizer.query(queryset, info)

class SupplierCertificateNode(DjangoObjectType):
    class Meta:
        model = SupplierCertificate
        fields = ["id", "file", "name", "type", "size", "created"]

    def resolve_file(self, info):
        if self.file and hasattr(self.file, 'url'):
            return info.context.build_absolute_uri(self.file.url)
        else:
            return ''

class SupplierSubClusterCodeNode(graphene.ObjectType):
    sub_cluster_code = graphene.Field(SubClusterCodeNode)
    minimum_of_value = graphene.Float()
    percentage = graphene.Float()

class SupplierConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    reach = graphene.Boolean()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_reach(root, info, **kwargs):
        try:
            key = info.context.headers.get('Authorization')
            user = None
            if key is not None:
                key = key.split(" ")[-1]
                token = Token.objects.filter(key=key).first()
                if token is not None:
                    user = token.user

            is_supplier = bool(user and user.isSupplier())
            if is_supplier:
                if user.supplier_sub_account.exists():
                    checked_supplier = user.supplier_sub_account.first().supplier
                else:
                    checked_supplier = user.supplier
            update_supplier_flash_sale = []
            for supplierEdgeNode in root.edges:
                supplier = supplierEdgeNode.node
                if not is_supplier or checked_supplier != supplier:
                    if hasattr(supplier, "supplier_flash_sale_list"):
                        supplier_flash_sale_list = supplier.supplier_flash_sale_list
                    else:
                        supplier_flash_sale_list = supplier.supplier_products.filter(
                            confirmed_status = ProductConfirmStatus.APPROVED,
                            type = ProductType.PRODUCT
                        ).order_by("id")
                    for supplier_flash_sale in supplier_flash_sale_list:
                        supplier_flash_sale.reach_number = supplier_flash_sale.reach_number + 1
                        update_supplier_flash_sale.append(supplier_flash_sale)
            
            SupplierProduct.objects.bulk_update(update_supplier_flash_sale, ["reach_number"])
            return True
        except:
            return False
    
class UserFollowingSupplierFilter(FilterSet):
    id = django_filters.NumberFilter(field_name='id', lookup_expr="exact")
    username = django_filters.CharFilter(method='username_filter')
    status = django_filters.ChoiceFilter(field_name="follow_status", lookup_expr="exact", choices=UserFollowingSupplierStatus.choices)
    short_name = django_filters.CharFilter(method='short_name_filter')
    class Meta:
        model = UserFollowingSupplier
        fields = []
    
    def username_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username=value)
        return queryset
    def short_name_filter(self, queryset, name, value):
        queryset = queryset.filter(user__short_name__contains=value)
        return queryset

class UserFollowingSupplierNode(DjangoObjectType):
    class Meta:
        model = UserFollowingSupplier
        filterset_class = UserFollowingSupplierFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class SupplierNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')
    supplier_sub_cluster_code_list =graphene.List(SupplierSubClusterCodeNode)
    supplier_product_list = graphene.List(SupplierProductNode)
    supplier_flash_sale_list = graphene.List(SupplierProductNode)
    supplier_all_type_product_list = graphene.List(SupplierProductNode)
    user_following_supplier = graphene.List(UserFollowingSupplierNode)
    is_followed = graphene.Boolean()

    class Meta:
        model = Supplier
        filterset_class = SupplierFilter
        interfaces = (CustomNode, UserInterface)
        connection_class = SupplierConnection

    def resolve_company_logo(self, info):
        if self.company_logo and hasattr(self.company_logo, 'url'):
            return info.context.build_absolute_uri(self.company_logo.url)
        else:
            return ''

    def resolve_picture(self, info):
        if self.picture and hasattr(self.picture, 'url'):
            return info.context.build_absolute_uri(self.picture.url)
        else:
            return ''

    def resolve_image_banner(self, info):
        if self.image_banner and hasattr(self.image_banner, 'url'):
            return info.context.build_absolute_uri(self.image_banner.url)
        else:
            return ''

    def resolve_supplier_sub_cluster_code_list(self, info):
        list_supplier_category = []
        if hasattr(self, "supplier_category_list"):
            list_supplier_category = self.supplier_category_list
        else:
            list_supplier_category = list(
                self.suppliercategory_set.all().select_related(
                    "category",
                    "category__sub_cluster_code"
                ).prefetch_related(
                    "category__sub_cluster_code__translations"
                )
            )
        if not len(list_supplier_category):
            return []
        
        sub_cluster_code_list = []
        result = []
        for supplier_category in list_supplier_category:
            if supplier_category.category.sub_cluster_code_id in sub_cluster_code_list:
                result[sub_cluster_code_list.index(supplier_category.category.sub_cluster_code_id)].minimum_of_value += supplier_category.minimum_of_value
                result[sub_cluster_code_list.index(supplier_category.category.sub_cluster_code_id)].percentage += supplier_category.percentage
            else:
                result.append(
                    SupplierSubClusterCodeNode(
                        sub_cluster_code = supplier_category.category.sub_cluster_code,
                        minimum_of_value = supplier_category.minimum_of_value,
                        percentage = supplier_category.percentage
                    )
                )
                sub_cluster_code_list.append(supplier_category.category.sub_cluster_code_id)
        return result

    def resolve_supplier_product_list(self, info, **kwargs):
        if hasattr(self, "supplier_product_list"):
            return self.supplier_product_list
        return self.supplier_products.filter(
            confirmed_status = ProductConfirmStatus.APPROVED,
            type = ProductType.PRODUCT
        ).order_by("id")

    def resolve_user_following_supplier(self, info, **kwargs):
        return self.user_supplier.filter(supplier_id = self.id)

    def resolve_supplier_flash_sale_list(self, info):
        if hasattr(self, "supplier_flash_sale_list"):
            return self.supplier_flash_sale_list

        return self.supplier_products.filter(
            confirmed_status = ProductConfirmStatus.APPROVED,
            type = ProductType.FLASH_SALE,
            is_visibility = True
        ).order_by("id")

    def resolve_supplier_all_type_product_list(self, info):
        if hasattr(self, "supplier_all_type_product_list"):
            return self.supplier_all_type_product_list

        return self.supplier_products.filter(
            confirmed_status = ProductConfirmStatus.APPROVED
        ).order_by("id")

    def resolve_is_followed(self, info):
        is_followed = False
        try:
            user = GetToken.getToken(info).user
            return self.user_supplier.filter(user_id=user.id, supplier_id=self.id, follow_status = UserFollowingSupplierStatus.FOLLOWING)
        except Exception as error:
            return is_followed

    @classmethod
    def get_queryset(cls, queryset, info):
        is_admin = False
        try:
            user = GetToken.getToken(info).user
            is_admin = user.isAdmin()
        except:
            is_admin = False
        query = Q()
        if not is_admin:
            query.add(Q(user__status=1), Q.AND)
        queryset = gql_optimizer.query(
            queryset.filter(query).prefetch_related(
                Prefetch(
                    "supplier_products",
                    queryset = SupplierProduct.objects.filter(
                        confirmed_status = ProductConfirmStatus.APPROVED,
                        type = ProductType.PRODUCT
                    ).select_related("payment_term", "unit_of_measure").prefetch_related(
                        "product_flash_sales",
                        "product_images",
                        "product_wholesale_price_list",
                        "payment_term__translations",
                        "unit_of_measure__translations",
                        Prefetch(
                            "supplier_product_category_list",
                            queryset = SupplierProductCategory.objects.all().select_related("category")
                        )
                    ),
                    to_attr = "supplier_product_list"
                ),
                Prefetch(
                    "supplier_products",
                    queryset = SupplierProduct.objects.filter(
                        confirmed_status = ProductConfirmStatus.APPROVED,
                        type = ProductType.FLASH_SALE,
                        is_visibility = True
                    ).select_related("payment_term", "unit_of_measure").prefetch_related(
                        "product_flash_sales",
                        "product_images",
                        "product_wholesale_price_list",
                        "payment_term__translations",
                        "unit_of_measure__translations",
                        Prefetch(
                            "supplier_product_category_list",
                            queryset = SupplierProductCategory.objects.all().select_related("category")
                        )
                    ).order_by("id"),
                    to_attr = "supplier_flash_sale_list"
                ),
                Prefetch(
                    "supplier_products",
                    queryset = SupplierProduct.objects.filter(
                        confirmed_status = ProductConfirmStatus.APPROVED
                    ).select_related("payment_term", "unit_of_measure").prefetch_related(
                        "product_flash_sales",
                        "product_images",
                        "product_wholesale_price_list",
                        "payment_term__translations",
                        "unit_of_measure__translations",
                        Prefetch(
                            "supplier_product_category_list",
                            queryset = SupplierProductCategory.objects.all().select_related("category")
                        )
                    ),
                    to_attr = "supplier_all_type_product_list"
                ),
                Prefetch(
                    "suppliercategory_set",
                    queryset = SupplierCategory.objects.all().select_related(
                        "category",
                        "category__sub_cluster_code"
                    ).prefetch_related(
                        "category__sub_cluster_code__translations"
                    ),
                    to_attr = "supplier_category_list"
                )
            ).order_by('id'),
            info
        )
        return queryset


class SupplierActivityNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = SupplierActivity
        interfaces = (CustomNode,)
        convert_choices_to_enum = False
        filter_fields = ['id', 'changed_by', 'changed_date', 'changed_state']
        connection_class = ExtendedConnection


class PortfolioNode(DjangoObjectType):
    class Meta:
        model = SupplierPortfolio
        filter_fields = ['id', 'company', 'project_name']
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_image(self, info):
        if self.image and hasattr(self.image, 'url'):
            return info.context.build_absolute_uri(self.image.url)
        else:
            return ''


class SupplierIndustryNode(DjangoObjectType):
    class Meta:
        model = SupplierIndustry
        filter_fields = [
            'id',
        ]
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection


class SupplierClientFocusNode(DjangoObjectType):
    class Meta:
        model = SupplierClientFocus
        filter_fields = [
            'id',
        ]
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection


class SupplierCategoryNode(DjangoObjectType):
    class Meta:
        model = SupplierCategory
        filter_fields = [
            'id',
        ]
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection


class SupplierCompanyCredentialNode(DjangoObjectType):
    class Meta:
        model = SupplierCompanyCredential
        filter_fields = [
            'id',
        ]
        interfaces = (relay.Node,)

    def resolve_company_credential_profile(self, info):
        if self.company_credential_profile and hasattr(self.company_credential_profile, 'url'):
            return info.context.build_absolute_uri(self.company_credential_profile.url)
        else:
            return ''


class SupplierBusinessLicenseNode(DjangoObjectType):
    class Meta:
        model = SupplierBusinessLicense
        filter_fields = [
            'id',
        ]
        interfaces = (relay.Node,)

    def resolve_business_license(self, info):
        if self.business_license and hasattr(self.business_license, 'url'):
            return info.context.build_absolute_uri(self.business_license.url)
        else:
            return ''


class SupplierFormRegistrationsNode(DjangoObjectType):
    class Meta:
        model = SupplierFormRegistrations
        filter_fields = [
            'id',
        ]
        interfaces = (relay.Node,)

    def resolve_form_registration(self, info):
        if self.form_registration and hasattr(self.form_registration, 'url'):
            return info.context.build_absolute_uri(self.form_registration.url)
        else:
            return ''


class SupplierQualityCertificationNode(DjangoObjectType):
    class Meta:
        model = SupplierQualityCertification
        filter_fields = [
            'id',
        ]
        interfaces = (relay.Node,)

    def resolve_quality_certification(self, info):
        if self.quality_certification and hasattr(self.quality_certification, 'url'):
            return info.context.build_absolute_uri(self.quality_certification.url)
        else:
            return ''


class SupplierTaxCertificationNode(DjangoObjectType):
    class Meta:
        model = SupplierTaxCertification
        filter_fields = [
            'id',
        ]
        interfaces = (relay.Node,)

    def resolve_tax_certification(self, info):
        if self.tax_certification and hasattr(self.tax_certification, 'url'):
            return info.context.build_absolute_uri(self.tax_certification.url)
        else:
            return ''


class SupplierBankCertificationNode(DjangoObjectType):
    class Meta:
        model = SupplierBankCertification
        filter_fields = [
            'id',
        ]
        interfaces = (relay.Node,)

    def resolve_bank_certification(self, info):
        if self.bank_certification and hasattr(self.bank_certification, 'url'):
            return info.context.build_absolute_uri(self.bank_certification.url)
        else:
            return ''


class SupplierOthersNode(DjangoObjectType):
    class Meta:
        model = SupplierOthers
        filter_fields = [
            'id',
        ]
        interfaces = (relay.Node,)

    def resolve_other(self, info):
        if self.other and hasattr(self.other, 'url'):
            return info.context.build_absolute_uri(self.other.url)
        else:
            return ''


class AuctionQuantityStatistics(graphene.ObjectType):
    used = graphene.Int()
    total = graphene.Int()

    def resolve_total(self, info):
        return self.profile_features.no_eauction_year

    def resolve_used(self, info):
        list_id = []
        if self.user.company_position == 1:
            list_sub_accounts = BuyerSubAccounts.objects.filter(buyer=self)
            for ob in list_sub_accounts:
                list_id.append(ob.user_id)
            list_id.append(self.user_id)
        else:
            buyer_sub_account = BuyerSubAccounts.objects.get(user=self.user)
            buyer = Buyer.objects.get(id=buyer_sub_account.buyer_id)
            buyer_auction = buyer.profile_features.no_eauction_year
            list_sub_accounts = BuyerSubAccounts.objects.filter(buyer=buyer)
            for ob in list_sub_accounts:
                list_id.append(ob.user_id)
            list_id.append(buyer.user_id)
        return Auction.objects.filter(user_id__in=list_id).count()


class BuyerNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')
    auction_quantity_statistics = graphene.Field(AuctionQuantityStatistics)

    class Meta:
        model = Buyer
        interfaces = (CustomNode, UserInterface)
        filterset_class = BuyerFilter
        connection_class = ExtendedConnection

    def resolve_company_logo(self, info):
        if self.company_logo and hasattr(self.company_logo, 'url'):
            return info.context.build_absolute_uri(self.company_logo.url)
        else:
            return ''

    def resolve_picture(self, info):
        if self.picture and hasattr(self.picture, 'url'):
            return info.context.build_absolute_uri(self.picture.url)
        else:
            return ''

    def resolve_auction_quantity_statistics(self, info):
        return self

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


class BuyerActivityNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = BuyerActivity
        interfaces = (CustomNode,)
        convert_choices_to_enum = False
        filterset_class = BuyerActivityFilter
        connection_class = ExtendedConnection


class BuyerIndustryNode(DjangoObjectType):
    class Meta:
        model = BuyerIndustry
        filter_fields = ['id']
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection


class UserInput(graphene.InputObjectType):
    password = graphene.String(required=True)
    email = graphene.String(required=True)
    short_name = graphene.String()
    full_name = graphene.String()
    status = graphene.Int(required=False)
    first_name = graphene.String()
    last_name = graphene.String()
    company_position = graphene.Int()
    username = graphene.String()


class BuyerSubAccountsActivityFilter(FilterSet):
    changed_by = django_filters.CharFilter(method='changed_by_filter')
    changed_date = django_filters.CharFilter(method='changed_date_filter')
    reason_manual = django_filters.CharFilter(method='reason_manual_filter')
    changed_state = django_filters.CharFilter(method='changed_state_filter')

    class Meta:
        model = BuyerSubAccounts
        fields = ['id']

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('changed_by__short_name', 'changed_by'),
            ('changed_date', 'changed_date'),
            ('reason_manual', 'reason_manual'),
            ('changed_state', 'changed_state'),
        )
    )

    def changed_by_filter(self, queryset, name, value):
        queryset = queryset.filter(changed_by__username__icontains=value)
        return queryset

    def changed_date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(changed_date__range=(value, value_to))
        return queryset

    def reason_manual_filter(self, queryset, name, value):
        queryset = queryset.filter(reason_manual__icontains=value)
        return queryset

    def changed_state_filter(self, queryset, name, value):
        queryset = queryset.filter(changed_state=value)
        return queryset


class BuyerSubAccountsActivityNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = BuyerSubAccountsActivity
        interfaces = (CustomNode,)
        convert_choices_to_enum = False
        filterset_class = BuyerSubAccountsActivityFilter
        connection_class = ExtendedConnection


class BuyerSubAccountsFilter(FilterSet):
    created = django_filters.CharFilter(method='created_filter')
    username = django_filters.CharFilter(method='username_filter')
    email = django_filters.CharFilter(method='email_filter')
    status = django_filters.CharFilter(method='status_filter')
    valid_from = django_filters.CharFilter(method='valid_from_filter')
    valid_to = django_filters.CharFilter(method='valid_to_filter')
    changed_by = django_filters.CharFilter(method='changed_by_filter')
    changed_date = django_filters.CharFilter(method='changed_date_filter')
    reason_manual = django_filters.CharFilter(method='reason_manual_filter')
    changed_state = django_filters.CharFilter(method='changed_state_filter')
    profile_feature = django_filters.CharFilter(method='profile_feature_filter')
    auctions_year = django_filters.CharFilter(method='auctions_year_filter')
    rfx_cancel = django_filters.CharFilter(method='rfx_cancel_filter')
    buyer_id = django_filters.CharFilter(method='buyer_id_filter')

    class Meta:
        model = BuyerSubAccounts
        fields = {
            'id': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('user__email', 'email'),
            ('user__created', 'created'),
            ('user__status', 'status'),
            ('user__username', 'username'),
            ('user__short_name', 'short_name'),
            ('buyer__profile_features__name', 'profile_features'),
            ('buyer__profile_features__no_eauction_year', 'auctions_year'),
            ('buyer__profile_features__rfx_year', 'rfx_cancel'),
            ('buyer__valid_from', 'valid_from'),
            ('buyer__valid_to', 'valid_to'),
        )
    )

    def email_filter(self, queryset, name, value):
        queryset = queryset.filter(user__email__icontains=value)
        return queryset

    def username_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username__icontains=value)
        return queryset

    def status_filter(self, queryset, name, value):
        queryset = queryset.filter(user__status=value)
        return queryset

    def created_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(user__created__range=(value, value_to))
        return queryset

    def valid_from_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(buyer__valid_from__gte=value)
        return queryset

    def valid_to_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(buyer__valid_to__lte=value)
        return queryset

    def profile_feature_filter(self, queryset, name, value):
        queryset = queryset.filter(buyer__profile_features_id=value)
        return queryset

    def auctions_year_filter(self, queryset, name, value):
        queryset = queryset.filter(buyer__profile_features__no_eauction_year=value)
        return queryset

    def rfx_cancel_filter(self, queryset, name, value):
        queryset = queryset.filter(buyer__profile_features__rfx_year=value)
        return queryset

    def changed_by_filter(self, queryset, name, value):
        list_system = []
        list_user_id = map(lambda x: x.get('id'), User.objects.filter(username__icontains=value).values('id'))
        list_id = map(
            lambda x: x.get('buyer_sub_accounts_id'),
            BuyerSubAccountsActivity.objects.filter(changed_by_id__in=list_user_id).values('buyer_sub_accounts_id'),
        )
        if value in "system":
            list_system = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(changed_by_id=None).values('supplier_id'))
        list_id = list(list_id) + list(list_system)
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        list_id = map(
            lambda x: x.get('buyer_sub_accounts_id'),
            BuyerSubAccountsActivity.objects.filter(changed_date__range=(value, value_to)).values('buyer_sub_accounts_id'),
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def reason_manual_filter(self, queryset, name, value):
        list_id = map(
            lambda x: x.get('buyer_sub_accounts_id'),
            BuyerSubAccountsActivity.objects.filter(reason_manual__icontains=value).values('buyer_sub_accounts_id'),
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_state_filter(self, queryset, name, value):
        list_id = map(
            lambda x: x.get('buyer_sub_accounts_id'), BuyerSubAccountsActivity.objects.filter(changed_state=value).values('buyer_sub_accounts_id')
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def buyer_id_filter(self, queryset, name, value):
        queryset = queryset.filter(buyer__id=value)
        return queryset


class BuyerSubAccountsNode(DjangoObjectType):
    class Meta:
        model = BuyerSubAccounts
        interfaces = (CustomNode, UserInterface)
        convert_choices_to_enum = False
        filterset_class = BuyerSubAccountsFilter
        connection_class = ExtendedConnection

    def resolve_picture(self, info):
        if self.picture and hasattr(self.picture, 'url'):
            return info.context.build_absolute_uri(self.picture.url)
        else:
            return ''

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


# --------------Buyer----------
class UserBuyerUpdateInput(graphene.InputObjectType):

    short_name = graphene.String()
    full_name = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    status = graphene.Int(required=False)


class BuyerInput(graphene.InputObjectType):
    company_short_name = graphene.String(required=True)
    company_long_name = graphene.String(required=True)
    company_logo = Upload()
    company_tax = graphene.String(required=True)
    company_address = graphene.String(required=True)
    company_city = graphene.String(required=True)
    company_country = graphene.String(required=True)
    company_country_state = graphene.String(required=True)
    company_number_of_employee = graphene.String(required=True)
    company_website = graphene.String(required=False)
    company_referral_code = graphene.String(required=False)
    company_email = graphene.String(required=True)
    gender = graphene.String(required=True)
    picture = Upload()
    phone = graphene.String(required=True)
    position = graphene.String(required=True)
    language = graphene.String(required=False)
    currency = graphene.String(required=True)
    profile_features = graphene.String(required=True)
    promotion = graphene.String()
    user = graphene.Field(UserInput, required=True)
    industries = graphene.List(graphene.String, required=True)


class BuyerUpdateInput(graphene.InputObjectType):
    company_short_name = graphene.String(required=True)
    company_long_name = graphene.String(required=True)
    company_logo = Upload()
    company_tax = graphene.String(required=True)
    company_address = graphene.String(required=True)
    company_city = graphene.String(required=True)
    company_country = graphene.String(required=True)
    company_country_state = graphene.String(required=True)
    company_number_of_employee = graphene.String(required=True)
    company_website = graphene.String(required=False)
    company_email = graphene.String(required=True)
    gender = graphene.String(required=True)
    picture = Upload()
    phone = graphene.String(required=True)
    position = graphene.String(required=True)
    language = graphene.String(required=False)
    currency = graphene.String(required=True)
    profile_features = graphene.String(required=True)
    promotion = graphene.String()
    user = graphene.Field(UserBuyerUpdateInput, required=True)
    industries = graphene.List(graphene.String, required=True)
    reason_manual = graphene.String()


class BuyerCreate(graphene.Mutation):
    class Arguments:
        user = UserInput(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(self, info, user):
        try:
            # Kiểm tra email đã tồn tại hay chưa
            if User.objects.filter(user_type=2, email=user.email).exists():
                raise GraphQLError('Email already exists')

            # Tạo username mới dựa trên số lượng người dùng
            user_count = User.objects.filter(user_type=2, company_position=1).count() + 1
            username = '80' + str(user_count).zfill(4)

            # Tạo đối tượng user mới
            new_user = User(
                username=username,
                user_type=2,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                company_position=user.company_position or 1,
            )
            new_user.set_password(user.password)
            new_user.save()

            # Tạo bản ghi thanh toán cho user
            UserPayment.objects.create(user=new_user)

            # Gửi email kích hoạt tài khoản
            email = EmailTemplates.objects.get(item_code='ActivateBuyerAccount')
            title = email.title

            t = Template(email.content)
            last_name = user.last_name if user.last_name is not None else ""
            first_name = user.first_name if user.first_name is not None else ""

            c = Context(
                {
                    "name": last_name + " " + first_name,
                    "username": username,
                    "password": user.password,
                }
            )

            output = t.render(c)

            try:
                send_mail(title, output, "NextPro <no-reply@nextpro.io>", [new_user.email], html_message=output, fail_silently=True)
            except:
                print("fail mail")

            return BuyerCreate(status=True)  # Không trả về thông tin buyer nếu không cần

        except Exception as errors:
            transaction.set_rollback(True)
            raise GraphQLError(str(errors))

class BuyerUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        buyer = BuyerUpdateInput(required=True)
        is_delete_logo = graphene.Boolean(required=True)
        is_delete_picture = graphene.Boolean(required=True)

    buyer = graphene.Field(BuyerNode)
    status = graphene.Boolean()

    def mutate(self, info, id, buyer, is_delete_logo, is_delete_picture):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            buyer_instance = Buyer.objects.get(pk=id)
            user = User.objects.get(pk=buyer_instance.user_id)
            user.first_name = buyer.user.first_name
            user.last_name = buyer.user.last_name
            user.status = buyer_instance.user.status

            profile_features = buyer_instance.profile_features_id
            if buyer.promotion is not None:
                promotion = buyer.promotion
                promotion_instance = Promotion.objects.get(id=promotion)
                if promotion_instance.status == False:
                    raise GraphQLError('Promotion code has been deactivated ')
                if promotion_instance.apply_for_buyer == False:
                    raise GraphQLError('This promotion does not apply for buyer')
                if promotion_instance.discount == 100:
                    profile_features = buyer.profile_features
            else:
                promotion = buyer_instance.promotion_id

            if buyer.picture is None and not is_delete_picture:
                picture = buyer_instance.picture
            else:
                picture = buyer.picture
            if buyer.company_logo is None and not is_delete_logo:
                company_logo = buyer_instance.company_logo
            else:
                company_logo = buyer.company_logo

            buyer_instance.company_short_name = buyer.company_short_name
            buyer_instance.company_long_name = buyer.company_long_name
            buyer_instance.company_logo = company_logo
            buyer_instance.company_tax = buyer.company_tax
            buyer_instance.company_address = buyer.company_address
            buyer_instance.company_city = buyer.company_city
            buyer_instance.company_country_id = buyer.company_country
            buyer_instance.company_country_state_id = buyer.company_country_state
            buyer_instance.company_number_of_employee_id = buyer.company_number_of_employee
            buyer_instance.company_website = buyer.company_website
            buyer_instance.company_email = buyer.company_email
            buyer_instance.gender_id = buyer.gender
            buyer_instance.picture = picture
            buyer_instance.phone = buyer.phone
            buyer_instance.position_id = buyer.position
            buyer_instance.language_id = buyer.language
            buyer_instance.currency_id = buyer.currency
            buyer_instance.profile_features_id = profile_features
            buyer_instance.promotion_id = promotion

            if len(buyer.industries) > 10:
                raise GraphQLError("Number industry  is less than or equals 10")

            buyer_industry_mapping = map(
                lambda x: x.get('industry_id'), BuyerIndustry.objects.filter(user_buyer_id=buyer_instance.id).values('industry_id')
            )
            buyer_industry_list = buyer_industry_list = map(lambda x: int(x), buyer.industries)
            buyer_industry_list = set(buyer_industry_list)
            buyer_industry_mapping = set(buyer_industry_mapping)

            buyer_industry_delete = buyer_industry_mapping.difference(buyer_industry_list)
            BuyerIndustry.objects.filter(industry_id__in=buyer_industry_delete, user_buyer_id=buyer_instance.id).delete()

            buyer_industry_create = buyer_industry_list.difference(buyer_industry_mapping)
            for industry_id in buyer_industry_create:
                industry_buyer = BuyerIndustry(industry_id=industry_id, user_buyer_id=buyer_instance.id)
                industry_buyer.save()

            buyer_instance.save()
            buyer_instance.user.first_name = user.first_name
            buyer_instance.user.last_name = user.last_name
            user.save()
            return BuyerUpdate(status=True, buyer=buyer_instance)
        else:
            raise GraphQLError('No permission')


class BuyerProfileUpdate(graphene.Mutation):
    class Arguments:
        buyer = BuyerUpdateInput(required=True)
        is_delete_logo = graphene.Boolean(required=True)
        is_delete_picture = graphene.Boolean(required=True)

    buyer = graphene.Field(BuyerNode)
    status = graphene.Boolean()

    def mutate(self, info, buyer, is_delete_logo, is_delete_picture):
        token = GetToken.getToken(info)
        buyer_instance = Buyer.objects.get(pk=token.user.buyer.id)
        user = User.objects.get(pk=buyer_instance.user_id)
        user.first_name = buyer.user.first_name
        user.last_name = buyer.user.last_name
        user.status = buyer_instance.user.status

        profile_features = buyer_instance.profile_features_id
        if buyer.promotion is not None:
            promotion = buyer.promotion
            promotion_instance = Promotion.objects.get(id=promotion)
            if promotion_instance.status == False:
                raise GraphQLError('Promotion code has been deactivated ')
            if promotion_instance.discount == 100:
                profile_features = buyer.profile_features
        else:
            promotion = buyer_instance.promotion_id

        if buyer.picture is None and not is_delete_picture:
            picture = buyer_instance.picture
        else:
            picture = buyer.picture
        if buyer.company_logo is None and not is_delete_logo:
            company_logo = buyer_instance.company_logo
        else:
            company_logo = buyer.company_logo

        buyer_instance.company_short_name = buyer.company_short_name
        buyer_instance.company_long_name = buyer.company_long_name
        buyer_instance.company_logo = company_logo
        buyer_instance.company_tax = buyer.company_tax
        buyer_instance.company_address = buyer.company_address
        buyer_instance.company_city = buyer.company_city
        buyer_instance.company_country_id = buyer.company_country
        buyer_instance.company_country_state_id = buyer.company_country_state
        buyer_instance.company_number_of_employee_id = buyer.company_number_of_employee
        buyer_instance.company_website = buyer.company_website
        buyer_instance.company_email = buyer.company_email
        buyer_instance.gender_id = buyer.gender
        buyer_instance.picture = picture
        buyer_instance.phone = buyer.phone
        buyer_instance.position_id = buyer.position
        buyer_instance.language_id = buyer.language
        buyer_instance.currency_id = buyer.currency
        buyer_instance.profile_features_id = profile_features
        buyer_instance.promotion_id = promotion

        if len(buyer.industries) > 10:
            raise GraphQLError("Number industry  is less than or equals 10")

        buyer_industry_mapping = map(
            lambda x: x.get('industry_id'), BuyerIndustry.objects.filter(user_buyer_id=buyer_instance.id).values('industry_id')
        )
        buyer_industry_list = buyer_industry_list = map(lambda x: int(x), buyer.industries)
        buyer_industry_list = set(buyer_industry_list)
        buyer_industry_mapping = set(buyer_industry_mapping)

        buyer_industry_delete = buyer_industry_mapping.difference(buyer_industry_list)
        BuyerIndustry.objects.filter(industry_id__in=buyer_industry_delete, user_buyer_id=buyer_instance.id).delete()

        buyer_industry_create = buyer_industry_list.difference(buyer_industry_mapping)
        for industry_id in buyer_industry_create:
            industry_buyer = BuyerIndustry(industry_id=industry_id, user_buyer_id=buyer_instance.id)
            industry_buyer.save()

        buyer_instance.save()
        buyer_instance.user.first_name = user.first_name
        buyer_instance.user.last_name = user.last_name
        user.save()
        return BuyerProfileUpdate(status=True, buyer=buyer_instance)


class BuyerStatusUpdateInput(graphene.InputObjectType):
    buyer_id = graphene.String(required=True)
    status = graphene.Int(required=True)


class BuyerStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        reason_manual = graphene.String()
        list_status = graphene.List(BuyerStatusUpdateInput, required=True)

    def mutate(root, info, list_status, reason_manual=None):
        token = GetToken.getToken(info)

        if token.user.isAdmin():
            for buyer_status in list_status:
                buyer = Buyer.objects.select_related('user').get(pk=buyer_status.buyer_id)
                buyer.user.status = buyer_status.status
                buyer_activity = BuyerActivity(
                    buyer=buyer, changed_by_id=token.user.id, reason_manual=reason_manual, changed_state=buyer_status.status
                )
                sub = BuyerSubAccounts.objects.filter(buyer=buyer)
                for x in sub:
                    if buyer.user.status == 3:
                        x.user.status = 3
                        x.user.save()
                buyer_activity.save()
                buyer.user.save()
            return BuyerStatusUpdate(status=True)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
            return BuyerStatusUpdate(status=False, error=error)


# ----------Buyer Sub Accounts---------
class BuyerSubAccountsInput(graphene.InputObjectType):
    gender = graphene.String(required=True)
    phone = graphene.String(required=True)
    language = graphene.String(required=True)
    position = graphene.String(required=True)
    picture = Upload()
    currency = graphene.String(required=True)
    user = graphene.Field(UserInput, required=True)

class BuyerSubAccountsCreate(graphene.Mutation):
    class Arguments:
        buyer_sub_accounts = BuyerSubAccountsInput(required=True)

    status = graphene.Boolean()
    buyer_sub_accounts = graphene.Field(BuyerSubAccountsNode)
    error = graphene.Field(Error)

    def mutate(self, info, buyer_sub_accounts):
        try:
            error = None
            try:
                token = GetToken.getToken(info)
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
            user = token.user
            buyer = user.buyer
            number_buyer_sub_accounts = buyer.profile_features.sub_user_accounts
            list_id = []
            list_sub_account = BuyerSubAccounts.objects.filter(buyer=buyer)
            for ob in list_sub_account:
                list_id.append(ob.buyer_id)

            count = len(list_id)
            if count < number_buyer_sub_accounts:
                if user.isBuyer() and user.company_position == 1:
                    if (User.objects.filter(user_type=2, email=buyer_sub_accounts.user.email)).exists():
                        error = Error(code="USER_01", message=UserError.USER_01)
                        raise GraphQLError('USER_01')

                    user_count = BuyerSubAccounts.objects.filter(buyer=buyer).count() + 1
                    username_sub_accounts = str(user.username)
                    username = username_sub_accounts + str("." + str(user_count)).zfill(1)
                    user_buyer = User(username=username, user_type=2, company_position=2, **buyer_sub_accounts.user)
                    user_buyer.set_password(buyer_sub_accounts.user.password)
                    user_buyer.save()
                    gender = buyer_sub_accounts.gender
                    language = buyer_sub_accounts.language
                    position = buyer_sub_accounts.position
                    currency = buyer_sub_accounts.currency

                    buyer_sub_account = BuyerSubAccounts.objects.create(
                        gender_id=gender,
                        phone=buyer_sub_accounts.phone,
                        language_id=language,
                        position_id=position,
                        picture=buyer_sub_accounts.picture,
                        currency_id=currency,
                        user=user_buyer,
                        buyer=user.buyer,
                    )
                    return BuyerSubAccountsCreate(status=True, buyer_sub_accounts=buyer_sub_account)
                else:
                    error = Error(code="USER_02", message=UserError.USER_02)
                    raise GraphQLError("USER_02")
            else:
                error = Error(code="USER_09", message=UserError.USER_09)
                raise GraphQLError("USER_09")
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return BuyerSubAccountsCreate(error=error, status=False)


class BuyerSubAccountsStatusUpdateInput(graphene.InputObjectType):
    buyer_sub_accounts_id = graphene.String(required=True)
    status = graphene.Int(required=True)


class BuyerSubAccountsStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(BuyerSubAccountsStatusUpdateInput, required=True)
        reason_manual = graphene.String()

    def mutate(root, info, list_status, reason_manual=None):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            for buyer_sub_accounts_status in list_status:
                buyer_sub_accounts = BuyerSubAccounts.objects.select_related('user').get(
                    pk=buyer_sub_accounts_status.buyer_sub_accounts_id
                )
                buyer_sub_accounts.user.status = buyer_sub_accounts_status.status
                buyer_sub_accounts_activity = BuyerSubAccountsActivity(
                    buyer_sub_accounts=buyer_sub_accounts,
                    changed_by_id=token.user.id,
                    reason_manual=reason_manual,
                    changed_state=buyer_sub_accounts_status.status,
                )
                buyer_sub_accounts_activity.save()
                buyer_sub_accounts.user.save()
            return BuyerSubAccountsStatusUpdate(status=True)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
            return BuyerSubAccountsStatusUpdate(status=False, error=error)


# ----------Supplier flash sale---------
class SupplierFlashSaleInput(graphene.InputObjectType):
    id = graphene.ID()
    sku_number = graphene.String()
    description = graphene.String()
    picture = Upload()
    initial_price = graphene.Float()
    percentage = graphene.Float()
    user_supplier = graphene.Int()


class SupplierFlashSaleCreateInput(graphene.InputObjectType):
    sku_number = graphene.String()
    description = graphene.String()
    picture = Upload(required=True)
    initial_price = graphene.Float()
    percentage = graphene.Float()
    user_supplier = graphene.Int()
    is_active = graphene.Boolean()
    is_confirmed = graphene.Int()
    text_editer = graphene.String()
    url_path = graphene.String()


class SupplierFlashSaleCreate(graphene.Mutation):
    class Arguments:
        input = SupplierFlashSaleCreateInput(required = True)

    status = graphene.Boolean(default_value = False)
    supplier_flash_sale = graphene.Field(SupplierFlashSaleNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        error = None
        
        try:
            user = GetToken.getToken(info).user
        except:
            error = Error(code="USER_12", message=UserError.USER_12)
            return SupplierFlashSaleCreate(status=False, error=error)

        if not (user.isAdmin() or user.isSupplier()):
            error = Error(code="USER_02", message=UserError.USER_02)
            return SupplierFlashSaleCreate(status=False, error=error)

        if "percentage" in input and input.percentage > 100:
            error = Error(code="USER_08", message=UserError.USER_08)
            return SupplierFlashSaleCreate(status=False, error=error)
    
        if user.isAdmin():
            user_supplier_id = input.user_supplier
        elif user.isSupplier():
            user_supplier_id = user.get_profile().id

        if input.get("sku_number") and SupplierFlashSale.objects.filter(
            sku_number = input.sku_number,
            user_supplier_id = user_supplier_id
        ).exists():
            return SupplierFlashSaleCreate(error=Error(code="USER_20", message=UserError.USER_20))

        flash_sale = SupplierFlashSale.objects.filter(user_supplier_id=user_supplier_id).order_by("-re_order").first()
        if flash_sale is None:
            count = 0
        else:
            count = flash_sale.re_order
        re_order = count + 1
        if user.isSupplier():
            profile_flash_sale = ProfileFeaturesSupplier.objects.filter(supplier=user_supplier_id).first()
            flash_sale_active = SupplierFlashSale.objects.filter(user_supplier_id=user_supplier_id, is_active = True, is_confirmed = 1).order_by("id").count()

            if input.is_active and flash_sale_active >= profile_flash_sale.flash_sale:
                error = Error(code="USER_19", message=UserError.USER_19)
                return SupplierFlashSaleCreate(status=False, error=error)
            supplier_flash_sale_instance = SupplierFlashSale(
                sku_number = input.sku_number,
                description = input.description if input.description is not None else '',
                picture = input.picture,
                initial_price = input.initial_price if input.initial_price is not None else 0,
                percentage = input.percentage if input.percentage is not None else 0,
                user_supplier_id = user_supplier_id,
                is_active = input.is_active if input.is_active is not None else True,
                is_confirmed = 2,
                text_editer = input.text_editer,
                re_order = re_order,
                url_path = input.url_path,
            )
            supplier_flash_sale_instance.save()
            return SupplierFlashSaleCreate(status=True, supplier_flash_sale=supplier_flash_sale_instance)
        else:
            supplier_flash_sale_instance = SupplierFlashSale(
                sku_number = input.sku_number,
                description = input.description,
                picture = input.picture,
                initial_price = input.initial_price,
                percentage = input.percentage,
                user_supplier_id = user_supplier_id,
                is_active = input.is_active,
                is_confirmed = 2,
                text_editer = input.text_editer,
                re_order = re_order,
                url_path = input.url_path,
            )
            supplier_flash_sale_instance.save()
            return SupplierFlashSaleCreate(status=True, supplier_flash_sale=supplier_flash_sale_instance)


class SupplierFlashSaleUpdateInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    sku_number = graphene.String()
    description = graphene.String()
    picture = Upload()
    initial_price = graphene.Float()
    percentage = graphene.Float()
    user_supplier = graphene.Int()
    is_active = graphene.Boolean()
    is_confirmed = graphene.Int()
    text_editer = graphene.String()
    url_path = graphene.String()

class SupplierFlashSaleUpdate(graphene.Mutation):
    class Arguments:
        input = SupplierFlashSaleUpdateInput(required=True)

    status = graphene.Boolean()
    supplier_flash_sale = graphene.Field(SupplierFlashSaleNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):

        error = None
        
        try:
            user = GetToken.getToken(info).user
        except:
            error = Error(code="USER_12", message=UserError.USER_12)
            return SupplierFlashSaleUpdate(status=False, error=error)

        if not (user.isAdmin() or user.isSupplier()):
            error = Error(code="USER_02", message=UserError.USER_02)
            return SupplierFlashSaleUpdate(status=False, error=error)

        if "percentage" in input and input.percentage > 100:
            error = Error(code="USER_08", message=UserError.USER_08)
            return SupplierFlashSaleUpdate(status=False, error=error)


        supplier_flash_sale_instance = SupplierFlashSale.objects.filter(id=input.id).first()
        if input.get("sku_number") and SupplierFlashSale.objects.filter(
            sku_number = input.sku_number,
            user_supplier_id = supplier_flash_sale_instance.user_supplier_id
        ).exclude(id=input.id).exists():
            return SupplierFlashSaleCreate(error=Error(code="USER_20", message=UserError.USER_20))
        
        sku_number = supplier_flash_sale_instance.sku_number
        description = supplier_flash_sale_instance.description
        picture = supplier_flash_sale_instance.picture
        initial_price = supplier_flash_sale_instance.initial_price
        percentage = supplier_flash_sale_instance.percentage
        is_active = supplier_flash_sale_instance.is_active
        is_confirmed = supplier_flash_sale_instance.is_confirmed
        re_order = supplier_flash_sale_instance.re_order
        text_editer = supplier_flash_sale_instance.text_editer
        url_path = supplier_flash_sale_instance.url_path

        profile_flash_sale = ProfileFeaturesSupplier.objects.filter(supplier=supplier_flash_sale_instance.user_supplier_id).first()
        flash_sale_active = SupplierFlashSale.objects.filter(user_supplier_id=supplier_flash_sale_instance.user_supplier_id, is_active = True, is_confirmed = 1).exclude(id=input.id).order_by("id").count()
        if flash_sale_active >= profile_flash_sale.flash_sale and input.is_active == True:
            error = Error(code="USER_19", message=UserError.USER_19)
            return SupplierFlashSaleUpdate(status=False, error=error)

        if supplier_flash_sale_instance is None:
            error = Error(code="USER_14", message=UserError.USER_14)
            return SupplierFlashSaleUpdate(status=False, error=error)

        if user.isAdmin():
            supplier = Supplier.objects.filter(id=supplier_flash_sale_instance.user_supplier_id).first()
            if user.id == supplier.user_id:
                for key, values in input.items():
                    if key in [f.name for f in SupplierFlashSale._meta.get_fields()]:
                        setattr(supplier_flash_sale_instance, key, values)
                supplier_flash_sale_instance.save()
                return SupplierFlashSaleUpdate(status=True, supplier_flash_sale=supplier_flash_sale_instance)
            else:
                supplier_flash_sale_instance.is_confirmed = input.is_confirmed
                supplier_flash_sale_instance.save()
                return SupplierFlashSaleUpdate(status=True, supplier_flash_sale=supplier_flash_sale_instance)
        elif user.isSupplier():               
            supplier = Supplier.objects.filter(id=supplier_flash_sale_instance.user_supplier_id).first()
            if user.id == supplier.user_id:
                for key, values in input.items():
                    if key in [f.name for f in SupplierFlashSale._meta.get_fields()]:
                        setattr(supplier_flash_sale_instance, key, values)
                supplier_flash_sale_instance.is_confirmed = 2
                supplier_flash_sale_instance.save()
                b = supplier_flash_sale_instance

                if b.sku_number == sku_number and b.description == description and b.picture == picture and b.initial_price == initial_price and b.percentage == percentage and b.re_order == re_order and b.text_editer == text_editer and b.url_path == url_path and is_confirmed != 3 and is_active == True and b.is_active == False:
                    b.is_confirmed = 1
                    b.save()
                
                if b.sku_number == sku_number and b.description == description and b.picture == picture and b.initial_price == initial_price and b.percentage == percentage and b.re_order == re_order and b.text_editer == text_editer and b.url_path == url_path and is_confirmed == 3 and is_active == True and b.is_active == False:
                    b.is_confirmed = 1
                    b.save()

                return SupplierFlashSaleUpdate(status=True, supplier_flash_sale=b)

class SupplierFlashSaleUpdateStatusInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    is_active = graphene.Boolean(required=True)


class SupplierFlashSaleUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(SupplierFlashSaleUpdateStatusInput, required=True)

    def mutate(root, info, list_status):

        for i in list_status:
            supplier_flash_sale = SupplierFlashSale.objects.filter(id=i.id).first()
            profile_flash_sale = ProfileFeaturesSupplier.objects.filter(supplier=supplier_flash_sale.user_supplier_id).first()
            flash_sale_active = SupplierFlashSale.objects.filter(user_supplier_id=supplier_flash_sale.user_supplier_id, is_active = True, is_confirmed = 1).order_by("id").count()

            if flash_sale_active >= profile_flash_sale.flash_sale and i.is_active == True:
                error = Error(code="USER_19", message=UserError.USER_19)
                return SupplierFlashSaleUpdateStatus(status=False, error=error)

            if supplier_flash_sale.is_confirmed != 3:
                if supplier_flash_sale.is_active == True and i.is_active == False:
                    supplier_flash_sale.is_active = i.is_active
                    supplier_flash_sale.is_confirmed = 1
                    supplier_flash_sale.save()
                else:
                    supplier_flash_sale.is_active = i.is_active
                    supplier_flash_sale.is_confirmed = 2
                    supplier_flash_sale.save()
            elif supplier_flash_sale.is_confirmed == 3 and supplier_flash_sale.is_active == True and i.is_active == False:
                supplier_flash_sale.is_active = i.is_active
                supplier_flash_sale.is_confirmed = 1
                supplier_flash_sale.save()
            else:
                supplier_flash_sale.is_active = i.is_active
                supplier_flash_sale.save()
        return SupplierFlashSaleUpdateStatus(status=True)

class SupplierFlashSaleIsConfirmedUpdateInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    is_confirmed = graphene.Int(required=True)


class SupplierFlashSaleIsConfirmedUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_is_confirmed = graphene.List(SupplierFlashSaleIsConfirmedUpdateInput, required=True)

    @transaction.atomic
    def mutate(root, info, list_is_confirmed):

        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_02", message=UserError.USER_02)
            return SupplierFlashSaleIsConfirmedUpdate(error=error,status=False)

        if token.user.isAdmin():
            for i in list_is_confirmed:
                flash_sale = SupplierFlashSale.objects.filter(id=i.id).first()
                profile_flash_sale = ProfileFeaturesSupplier.objects.filter(supplier=flash_sale.user_supplier_id).first()
                flash_sale_active = SupplierFlashSale.objects.filter(user_supplier_id=flash_sale.user_supplier_id, is_active = True, is_confirmed = 1).order_by("id").count()

                if i.is_confirmed == 1 and flash_sale_active >= profile_flash_sale.flash_sale:
                    transaction.set_rollback(True)
                    error = Error(code="USER_19", message=UserError.USER_19)
                    return SupplierFlashSaleUpdateStatus(status=False, error=error)
                flash_sale.is_confirmed = i.is_confirmed
                flash_sale.save()
            return SupplierFlashSaleIsConfirmedUpdate(status=True)
        else:
            error = Error(code="USER_12", message=UserError.USER_12)
            return SupplierFlashSaleIsConfirmedUpdate(error=error,status=False)


class SupplierFlashSaleTextEditer(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        text_editer = graphene.String(required=True)

    def mutate(root, info, text_editer):
        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_02", message=UserError.USER_02)
            return SupplierFlashSaleTextEditer(error=error,status=False)

        if token.user.isAdmin():
            flash_sale_ids = map(
            lambda x: x.get('id'), SupplierFlashSale.objects.all().values('id')
            )
            for i in flash_sale_ids:
                flash_sale = SupplierFlashSale.objects.filter(id=i).first()
                flash_sale.text_editer = text_editer
                flash_sale.save()
            return SupplierFlashSaleTextEditer(status=True)
        else:
            error = Error(code="USER_12", message=UserError.USER_12)
            return SupplierFlashSaleTextEditer(error=error,status=False)

class SupplierFlashSaleUpdateOrderInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    re_order = graphene.Int()

class SupplierFlashSaleUpdateOrder(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_re_order = graphene.List(SupplierFlashSaleUpdateOrderInput, required=True)

    def mutate(root, info, list_re_order):
        user = GetToken.getToken(info).user
        re_orders = map(
            lambda x: x.get('re_order'), SupplierFlashSale.objects.filter(user_supplier_id__user_id=user.id).values('re_order')
        )
        flag = False
        for i in list_re_order:
            for j in re_orders:
                flash_sale = SupplierFlashSale.objects.filter(re_order=j).first()
                supplier = Supplier.objects.filter(id=flash_sale.user_supplier_id).first()
                if user.id == supplier.user_id:
                    if j <= i.re_order:
                        j = j - 1
                        flash_sale.re_order = j
                        flash_sale.save()
                        if j == i.re_order:
                            flag = True
                    if flag == False:
                        if j >= i.re_order:
                            j = j + 1
                            flash_sale.re_order = j
                            flash_sale.save()
            supplier_flash_sale = SupplierFlashSale.objects.filter(id=i.id).first()
            supplier_flash_sale.re_order = i.re_order
            supplier_flash_sale.save()
        return SupplierFlashSaleUpdateOrder(status=True)


class SupplierFlashSaleDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(root, info, **kwargs):
        supplier_flash_sale = SupplierFlashSale.objects.get(pk=kwargs["id"])
        supplier_flash_sale.delete()
        return SupplierFlashSaleDelete(status=True)


class CategorySupplierInput(graphene.InputObjectType):
    percentage = graphene.Int(required=True)
    minimum_of_value = graphene.Int(required=True)
    category = graphene.String(required=True)


class SupplierIndustryInput(graphene.InputObjectType):
    industry_sub_sectors = graphene.String(required=True)
    percentage = graphene.Int(required=True)


class ClientFocusInputSupplier(graphene.InputObjectType):
    client_focus = graphene.String(required=True)
    percentage = graphene.Int(required=True)


class PortfoliosInput(graphene.InputObjectType):
    project_name = graphene.String(required=True)
    company = graphene.String(required=True)
    value = graphene.Int(required=True)
    project_description = graphene.String(required=True)
    image = Upload()


class SupplierInput(graphene.InputObjectType):
    company_short_name = graphene.String(required=True)
    company_long_name = graphene.String(required=True)
    company_tax = graphene.String(required=True)
    company_logo = Upload()
    company_address = graphene.String(required=True)
    company_city = graphene.String(required=True)
    company_country = graphene.String(required=True)
    company_country_state = graphene.String(required=True)
    company_ceo_owner_name = graphene.String()
    company_ceo_owner_email = graphene.String()
    company_number_of_employee = graphene.String(required=True)
    company_website = graphene.String()
    company_credential_profiles = graphene.List(Upload, required=True)
    gender = graphene.String(required=True)
    phone = graphene.String(required=True)
    language = graphene.String(required=True)
    position = graphene.String(required=True)
    picture = Upload()
    currency = graphene.String(required=True)
    bank_name = graphene.String(required=True)
    beneficiary_name = graphene.String(required=True)
    bank_account_number = graphene.String(required=True)
    bank_code = graphene.String(required=True)
    switch_bic_code = graphene.String(required=True)
    international_bank = graphene.String()
    bank_address = graphene.String(required=True)
    bank_currency = graphene.String()
    user = graphene.Field(UserInput, required=True)
    company_tag_line = graphene.String()
    company_description = graphene.String(required=True)
    company_established_since = graphene.String(required=True)
    company_anniversary_date = graphene.String()
    supplier_form_registrations = graphene.List(Upload, required=True)
    bank_certifications = graphene.List(Upload, required=True)
    quality_certifications = graphene.List(Upload, required=True)
    business_licenses = graphene.List(Upload, required=True)
    tax_certifications = graphene.List(Upload, required=True)
    others = graphene.List(Upload, required=True)
    profile_features = graphene.String(required=True)
    sicp_registration = graphene.String(required=True)
    core_business = graphene.List(graphene.List(CategorySupplierInput, required=True))
    industries = graphene.List(SupplierIndustryInput, required=True)
    client_focus = graphene.List(ClientFocusInputSupplier, required=True)
    portfolios = graphene.List(PortfoliosInput, required=True)
    promotion = graphene.String()


class SupplierCreate(graphene.Mutation):
    class Arguments:
        supplier = SupplierInput(required=True)

    status = graphene.Boolean()
    supplier = graphene.Field(SupplierNode)

    def mutate(self, info, supplier):
        try:
            if (User.objects.filter(user_type=3, email=supplier.user.email)).exists():
                raise GraphQLError('Email already exists')
            user_count = User.objects.filter(user_type=3).count() + 1
            username = '90' + str(user_count).zfill(4)
            user = User(username=username, user_type=3, **supplier.user)
            user.set_password(supplier.user.password)
            user.save()
            profile_features = 1
            sicp_registration = 1
            if supplier.promotion is not None:
                promotion = supplier.promotion
                promotion_instance = Promotion.objects.get(id=promotion)
                if promotion_instance.status == False:
                    raise GraphQLError('Promotion code has been deactivated ')
                if promotion_instance.discount == 100:
                    profile_features = supplier.profile_features
                    sicp_registration = supplier.sicp_registration
            else:
                promotion = None

            supplier_instance = Supplier(
                company_short_name=supplier.company_short_name,
                company_long_name=supplier.company_long_name,
                company_logo=supplier.company_logo,
                company_tax=supplier.company_tax,
                company_address=supplier.company_address,
                company_city=supplier.company_city,
                company_country_id=supplier.company_country,
                company_country_state_id=supplier.company_country_state,
                company_ceo_owner_name=supplier.company_ceo_owner_name,
                company_ceo_owner_email=supplier.company_ceo_owner_email,
                company_number_of_employee_id=supplier.company_number_of_employee,
                company_website=supplier.company_website,
                company_tag_line=supplier.company_tag_line,
                company_description=supplier.company_description,
                company_established_since=supplier.company_established_since,
                company_anniversary_date=supplier.company_anniversary_date,
                gender_id=supplier.gender,
                phone=supplier.phone,
                position_id=supplier.position,
                picture=supplier.picture,
                language_id=supplier.language,
                currency_id=supplier.currency,
                bank_name=supplier.bank_name,
                bank_code=supplier.bank_code,
                bank_address=supplier.bank_address,
                beneficiary_name=supplier.beneficiary_name,
                switch_bic_code=supplier.switch_bic_code,
                bank_currency_id=supplier.bank_currency,
                bank_account_number=supplier.bank_account_number,
                international_bank=supplier.international_bank,
                profile_features_id=profile_features,
                sicp_registration_id=sicp_registration,
                promotion_id=promotion,
                user=user,
            )
            supplier_instance.save()

            for company_credential in supplier.company_credential_profiles:
                company_credential_instance = SupplierCompanyCredential(supplier=supplier_instance, company_credential_profile=company_credential)
                company_credential_instance.save()

            for supplier_form_registration in supplier.supplier_form_registrations:
                form_registration_instance = SupplierFormRegistrations(supplier=supplier_instance, form_registration=supplier_form_registration)
                form_registration_instance.save()

            for supplier_bank_certification in supplier.bank_certifications:
                bank_certification_instance = SupplierBankCertification(supplier=supplier_instance, bank_certification=supplier_bank_certification)
                bank_certification_instance.save()

            for supplier_quality_certification in supplier.quality_certifications:
                quality_certification_instance = SupplierQualityCertification(
                    supplier=supplier_instance, quality_certification=supplier_quality_certification
                )
                quality_certification_instance.save()

            for supplier_business_license in supplier.business_licenses:
                business_license_instance = SupplierBusinessLicense(supplier=supplier_instance, business_license=supplier_business_license)
                business_license_instance.save()

            for supplier_tax_certification in supplier.tax_certifications:
                tax_certification_instance = SupplierTaxCertification(supplier=supplier_instance, tax_certification=supplier_tax_certification)
                tax_certification_instance.save()

            for supplier_other in supplier.others:
                other_instance = SupplierOthers(supplier=supplier_instance, other=supplier_other)
                other_instance.save()

            percentage_category = 0
            for categories in supplier.core_business:
                if len(categories) > 10:
                    raise GraphQLError("Number category  is less than or equals 10")
                for category in categories:
                    percentage_category += category.percentage
            if percentage_category != 100:
                raise GraphQLError("Total percentage core business must be equals 100")
            for categories in supplier.core_business:
                for category in categories:
                    category_instance = SupplierCategory(
                        percentage=category.percentage,
                        minimum_of_value=category.minimum_of_value,
                        user_supplier_id=supplier_instance.id,
                        category_id=category.category,
                    )
                    category_instance.save()

            if len(supplier.industries) > 10:
                raise GraphQLError("Number industry  is less than or equals 10")

            percentage_industry = 0
            for industry in supplier.industries:
                percentage_industry += industry.percentage

            percentage_client_focus = 0
            for client_focus in supplier.client_focus:
                percentage_client_focus += client_focus.percentage

            if percentage_client_focus != 100 or percentage_industry != 100:
                raise GraphQLError("Total percentage must be equals 100")

            for industry in supplier.industries:
                industry_instance = SupplierIndustry(
                    percentage=industry.percentage,
                    industry_sub_sectors_id=industry.industry_sub_sectors,
                    user_supplier_id=supplier_instance.id,
                )
                industry_instance.save()

            for client_focus in supplier.client_focus:
                client_focus_intance = SupplierClientFocus(
                    percentage=client_focus.percentage,
                    client_focus_id=client_focus.client_focus,
                    user_supplier_id=supplier_instance.id,
                )
                client_focus_intance.save()

            for portfolio in supplier.portfolios:
                portfolio_instance = SupplierPortfolio(
                    company=portfolio.company,
                    project_name=portfolio.project_name,
                    value=portfolio.value,
                    project_description=portfolio.project_description,
                    image=portfolio.image,
                    user_supplier_id=supplier_instance.id,
                )
                portfolio_instance.save()
            UserPayment.objects.create(user=user)

            email = EmailTemplates.objects.get(item_code='ActivateSupplierAccount')
            title = email.title

            t = Template(email.content)
            c = Context(
                {
                    "image": info.context.build_absolute_uri("/static/logo_mail.png"),
                    "name": user.last_name + " " + user.first_name,
                    "password": supplier.user.password,
                    "username": user.username,
                }
            )
            output = t.render(c)
            try:
                send_mail(title, output, "NextPro <no-reply@nextpro.io>", [user.email], html_message=output, fail_silently=True)
            except:
                print("Fail mail")

            return SupplierCreate(status=True, supplier=supplier_instance)
        except Exception as errors:
            transaction.set_rollback(True)
            return SupplierCreate(errors)


class UserSupplierInput(graphene.InputObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    status = graphene.Int(required=False)


class PortfoliosUpdateInput(graphene.InputObjectType):
    id = graphene.String()
    project_name = graphene.String(required=True)
    company = graphene.String(required=True)
    value = graphene.Int(required=True)
    project_description = graphene.String(required=True)
    image = Upload()
    is_delete_image = graphene.Boolean()


class IsDelete(graphene.InputObjectType):
    picture = graphene.Boolean(required=True)
    company_logo = graphene.Boolean(required=True)
    company_credential_profiles = graphene.Boolean(required=True)
    supplier_form_registrations = graphene.Boolean(required=True)
    bank_certifications = graphene.Boolean(required=True)
    quality_certifications = graphene.Boolean(required=True)
    business_licenses = graphene.Boolean(required=True)
    tax_certifications = graphene.Boolean(required=True)
    others = graphene.Boolean(required=True)


class SupplierUpdateInput(graphene.InputObjectType):
    company_short_name = graphene.String(required=True)
    company_long_name = graphene.String(required=True)
    company_tax = graphene.String(required=True)
    company_logo = Upload()
    company_address = graphene.String(required=True)
    company_city = graphene.String(required=True)
    company_country = graphene.String(required=True)
    company_country_state = graphene.String(required=True)
    company_ceo_owner_name = graphene.String()
    company_ceo_owner_email = graphene.String()
    company_number_of_employee = graphene.String(required=True)
    company_website = graphene.String()
    company_credential_profiles = graphene.List(Upload, required=True)
    gender = graphene.String(required=True)
    phone = graphene.String(required=True)
    language = graphene.String(required=True)
    position = graphene.String(required=True)
    picture = Upload()
    currency = graphene.String(required=True)
    bank_name = graphene.String(required=True)
    beneficiary_name = graphene.String(required=True)
    bank_account_number = graphene.String(required=True)
    bank_code = graphene.String(required=True)
    switch_bic_code = graphene.String(required=True)
    international_bank = graphene.String()
    bank_address = graphene.String(required=True)
    bank_currency = graphene.String()
    user = graphene.Field(UserSupplierInput, required=True)
    company_tag_line = graphene.String()
    company_description = graphene.String(required=True)
    company_established_since = graphene.String(required=True)
    company_anniversary_date = graphene.String()
    supplier_form_registrations = graphene.List(Upload, required=True)
    bank_certifications = graphene.List(Upload, required=True)
    quality_certifications = graphene.List(Upload, required=True)
    business_licenses = graphene.List(Upload, required=True)
    tax_certifications = graphene.List(Upload, required=True)
    others = graphene.List(Upload, required=True)
    profile_features = graphene.String(required=True)
    sicp_registration = graphene.String(required=True)
    core_business = graphene.List(graphene.List(CategorySupplierInput, required=True))
    industries = graphene.List(SupplierIndustryInput, required=True)
    client_focus = graphene.List(ClientFocusInputSupplier, required=True)
    portfolios = graphene.List(PortfoliosUpdateInput, required=True)
    promotion = graphene.String()
    is_delete = graphene.Field(IsDelete, required=True)
    portfolios_delete = graphene.List(graphene.String, required=False)


class SupplierUpdate(graphene.Mutation):
    class Arguments:
        supplier = SupplierUpdateInput(required=True)
        id = graphene.String(required=True)

    status = graphene.Boolean()
    supplier = graphene.Field(SupplierNode)

    def mutate(self, info, supplier, id):
        try:
            supplier_instance = Supplier.objects.get(pk=id)
            user = User.objects.get(pk=supplier_instance.user_id)
            user.first_name = supplier.user.first_name
            user.last_name = supplier.user.last_name
            user.status = supplier_instance.user.status
            user.save()

            if supplier.picture is None and not supplier.is_delete.picture:
                picture = supplier_instance.picture
            else:
                picture = supplier.picture

            if supplier.company_logo is None and not supplier.is_delete.company_logo:
                company_logo = supplier_instance.company_logo
            else:
                company_logo = supplier.company_logo

            profile_features = supplier_instance.profile_features_id
            sicp_registration = supplier_instance.profile_features_id
            if supplier.promotion is not None:
                promotion = supplier.promotion
                promotion_instance = Promotion.objects.get(id=promotion)
                if promotion_instance.status == False:
                    raise GraphQLError('Promotion code has been deactivated ')
                if promotion_instance.apply_for_supplier == False:
                    raise GraphQLError('This promotion does not apply for supplier')
                if promotion_instance.discount == 100:
                    profile_features = supplier.profile_features
                    sicp_registration = supplier.sicp_registration
            else:
                promotion = supplier_instance.promotion_id

            supplier_instance.company_short_name = supplier.company_short_name
            supplier_instance.company_long_name = supplier.company_long_name
            supplier_instance.company_logo = company_logo
            supplier_instance.company_tax = supplier.company_tax
            supplier_instance.company_address = supplier.company_address
            supplier_instance.company_city = supplier.company_city
            supplier_instance.company_country_id = supplier.company_country
            supplier_instance.company_country_state_id = supplier.company_country_state
            supplier_instance.company_ceo_owner_name = supplier.company_ceo_owner_name
            supplier_instance.company_ceo_owner_email = supplier.company_ceo_owner_email
            supplier_instance.company_number_of_employee_id = supplier.company_number_of_employee
            supplier_instance.company_website = supplier.company_website
            supplier_instance.company_tag_line = supplier.company_tag_line
            supplier_instance.company_description = supplier.company_description
            supplier_instance.company_established_since = supplier.company_established_since
            supplier_instance.company_anniversary_date = supplier.company_anniversary_date
            supplier_instance.gender_id = supplier.gender
            supplier_instance.phone = supplier.phone
            supplier_instance.position_id = supplier.position
            supplier_instance.picture = picture
            supplier_instance.language_id = supplier.language
            supplier_instance.currency_id = supplier.currency
            supplier_instance.bank_name = supplier.bank_name
            supplier_instance.bank_code = supplier.bank_code
            supplier_instance.bank_address = supplier.bank_address
            supplier_instance.beneficiary_name = supplier.beneficiary_name
            supplier_instance.switch_bic_code = supplier.switch_bic_code
            supplier_instance.bank_currency_id = supplier.bank_currency
            supplier_instance.bank_account_number = supplier.bank_account_number
            supplier_instance.international_bank = supplier.international_bank
            supplier_instance.profile_features_id = profile_features
            supplier_instance.sicp_registration_id = sicp_registration
            supplier_instance.promotion_id = promotion

            supplier_instance.save()
            supplier_instance.user.last_name = user.last_name
            supplier_instance.user.first_name = user.first_name

            if supplier.is_delete.company_credential_profiles:
                SupplierCompanyCredential.objects.filter(supplier_id=supplier_instance.id).delete()
                for company_credential in supplier.company_credential_profiles:
                    company_credential_instance = SupplierCompanyCredential(supplier=supplier_instance, company_credential_profile=company_credential)
                    company_credential_instance.save()

            if supplier.is_delete.supplier_form_registrations:
                SupplierFormRegistrations.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_form_registration in supplier.supplier_form_registrations:
                    form_registration_instance = SupplierFormRegistrations(supplier=supplier_instance, form_registration=supplier_form_registration)
                    form_registration_instance.save()

            if supplier.is_delete.bank_certifications:
                SupplierBankCertification.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_bank_certification in supplier.bank_certifications:
                    bank_certification_instance = SupplierBankCertification(
                        supplier=supplier_instance, bank_certification=supplier_bank_certification
                    )
                    bank_certification_instance.save()

            if supplier.is_delete.quality_certifications:
                SupplierQualityCertification.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_quality_certification in supplier.quality_certifications:
                    quality_certification_instance = SupplierQualityCertification(
                        supplier=supplier_instance, quality_certification=supplier_quality_certification
                    )
                    quality_certification_instance.save()

            if supplier.is_delete.business_licenses:
                SupplierBusinessLicense.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_business_license in supplier.business_licenses:
                    business_license_instance = SupplierBusinessLicense(supplier=supplier_instance, business_license=supplier_business_license)
                    business_license_instance.save()

            if supplier.is_delete.tax_certifications:
                SupplierTaxCertification.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_tax_certification in supplier.tax_certifications:
                    tax_certification_instance = SupplierTaxCertification(supplier=supplier_instance, tax_certification=supplier_tax_certification)
                    tax_certification_instance.save()

            if supplier.is_delete.others:
                SupplierOthers.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_other in supplier.others:
                    other_instance = SupplierOthers(supplier=supplier_instance, other=supplier_other)
                    other_instance.save()

            percentage_category = 0
            for categories in supplier.core_business:
                if len(categories) > 10:
                    raise GraphQLError("Number category  is less than or equals 10")
                for category in categories:
                    percentage_category += category.percentage
            if percentage_category != 100:
                raise GraphQLError("Total percentage core business must be equals 100")
            for categories in supplier.core_business:
                for category in categories:
                    category_mapping = SupplierCategory.objects.filter(
                        user_supplier_id=supplier_instance.id, category_id=category.category
                    )
                    if category_mapping.exists():
                        category_mapping = category_mapping.first()
                        category_mapping.percentage = category.percentage
                        category_mapping.minimum_of_value = category.minimum_of_value
                        category_mapping.save()
                    else:
                        category_instance = SupplierCategory(
                            percentage=category.percentage,
                            minimum_of_value=category.minimum_of_value,
                            user_supplier_id=supplier_instance.id,
                            category_id=category.category,
                        )
                        category_instance.save()

            if len(supplier.industries) > 10:
                raise GraphQLError("Number industry  is less than or equals 10")

            percentage_industry = 0
            for industry in supplier.industries:
                percentage_industry += industry.percentage

            percentage_client_focus = 0
            for client_focus in supplier.client_focus:
                percentage_client_focus += client_focus.percentage

            if percentage_client_focus != 100 or percentage_industry != 100:
                raise GraphQLError("Total percentage must be equals 100")

            for industry in supplier.industries:
                industry_mapping = SupplierIndustry.objects.filter(
                    industry_sub_sectors_id=industry.industry_sub_sectors, user_supplier_id=supplier_instance.id
                )
                if industry_mapping.exists():
                    industry_mapping = industry_mapping.first()
                    industry_mapping.percentage = industry.percentage
                    industry_mapping.save()
                else:
                    industry_instance = SupplierIndustry(
                        percentage=industry.percentage,
                        industry_sub_sectors_id=industry.industry_sub_sectors,
                        user_supplier_id=supplier_instance.id,
                    )
                    industry_instance.save()

            for client_focus in supplier.client_focus:
                client_focus_mapping = SupplierClientFocus.objects.filter(
                    client_focus_id=client_focus.client_focus, user_supplier_id=supplier_instance.id
                )
                if client_focus_mapping.exists():
                    client_focus_mapping = client_focus_mapping.first()
                    client_focus_mapping.percentage = client_focus.percentage
                    client_focus_mapping.save()
                else:
                    client_focus_intance = SupplierClientFocus(
                        percentage=client_focus.percentage,
                        client_focus_id=client_focus.client_focus,
                        user_supplier_id=supplier_instance.id,
                    )
                    client_focus_intance.save()

            # delete category
            list_category_mapping = map(
                lambda x: int(x.get('category_id')), SupplierCategory.objects.filter(user_supplier_id=supplier_instance.id).values('category_id')
            )
            list_category_mapping = set(list_category_mapping)
            list_category = []
            for categories in supplier.core_business:
                for category in categories:
                    list_category.append(int(category.category))
            list_category = set(list_category)
            list_delete = list_category_mapping.difference(list_category)
            SupplierCategory.objects.filter(user_supplier_id=supplier_instance.id, category_id__in=list_delete).delete()

            #  delete industry
            list_industry_mapping = map(
                lambda x: x.get('industry_sub_sectors_id'),
                SupplierIndustry.objects.filter(user_supplier_id=supplier_instance.id).values('industry_sub_sectors_id'),
            )
            list_industry_mapping = set(list_industry_mapping)
            list_industry = []
            for industry in supplier.industries:
                list_industry.append(int(industry.industry_sub_sectors))
            list_industry = set(list_industry)
            list_delete = list_industry_mapping.difference(list_industry)
            SupplierIndustry.objects.filter(user_supplier_id=supplier_instance.id, industry_sub_sectors_id__in=list_delete).delete()

            #  delete client focus
            list_client_focus_mapping = map(
                lambda x: x.get('client_focus_id'),
                SupplierClientFocus.objects.filter(user_supplier_id=supplier_instance.id).values('client_focus_id'),
            )
            list_client_focus_mapping = set(list_client_focus_mapping)
            list_client_focus = []
            for client_focus in supplier.client_focus:
                list_client_focus.append(int(client_focus.client_focus))
            list_client_focus = set(list_client_focus)
            list_delete = list_client_focus_mapping.difference(list_client_focus)
            SupplierClientFocus.objects.filter(user_supplier_id=supplier_instance.id, client_focus_id__in=list_delete).delete()

            # portfolio
            for portfolio_delete in supplier.portfolios_delete:
                SupplierPortfolio.objects.get(id=portfolio_delete).delete()
            for portfolio in supplier.portfolios:
                if portfolio.id is not None:
                    portfolio_mapping = SupplierPortfolio.objects.get(id=portfolio.id)
                    portfolio_mapping.company = portfolio.company
                    portfolio_mapping.project_name = portfolio.project_name
                    portfolio_mapping.value = portfolio.value
                    portfolio_mapping.project_description = portfolio.project_description
                    if portfolio.image is None and not portfolio.is_delete_image:
                        image = portfolio_mapping.image
                    else:
                        image = portfolio.image
                    portfolio_mapping.image = image
                    portfolio_mapping.save()
                else:
                    portfolio_instance = SupplierPortfolio(
                        company=portfolio.company,
                        project_name=portfolio.project_name,
                        value=portfolio.value,
                        project_description=portfolio.project_description,
                        image=portfolio.image,
                        user_supplier_id=supplier_instance.id,
                    )
                    portfolio_instance.save()

            return SupplierUpdate(status=True, supplier=supplier_instance)
        except Exception as errors:
            transaction.set_rollback(True)
            return SupplierUpdate(errors)


class SupplierProfileUpdate(graphene.Mutation):
    class Arguments:
        supplier = SupplierUpdateInput(required=True)

    status = graphene.Boolean()
    supplier = graphene.Field(SupplierNode)

    def mutate(self, info, supplier):
        try:
            id = GetToken.getToken(info).user.supplier.id
            supplier_instance = Supplier.objects.get(pk=id)
            user = User.objects.get(pk=supplier_instance.user_id)
            user.first_name = supplier.user.first_name
            user.last_name = supplier.user.last_name
            user.status = supplier_instance.user.status
            user.save()

            if supplier.picture is None and not supplier.is_delete.picture:
                picture = supplier_instance.picture
            else:
                picture = supplier.picture

            if supplier.company_logo is None and not supplier.is_delete.company_logo:
                company_logo = supplier_instance.company_logo
            else:
                company_logo = supplier.company_logo

            profile_features = supplier_instance.profile_features_id
            sicp_registration = supplier_instance.sicp_registration_id
            if supplier.promotion is not None:
                promotion = supplier.promotion
                promotion_instance = Promotion.objects.get(id=promotion)
                if promotion_instance.status == False:
                    raise GraphQLError('Promotion code has been deactivated ')
                if promotion_instance.discount == 100:
                    profile_features = supplier.profile_features
                    sicp_registration = supplier.sicp_registration
            else:
                promotion = supplier_instance.promotion_id

            supplier_instance.company_short_name = supplier.company_short_name
            supplier_instance.company_long_name = supplier.company_long_name
            supplier_instance.company_logo = company_logo
            supplier_instance.company_tax = supplier.company_tax
            supplier_instance.company_address = supplier.company_address
            supplier_instance.company_city = supplier.company_city
            supplier_instance.company_country_id = supplier.company_country
            supplier_instance.company_country_state_id = supplier.company_country_state
            supplier_instance.company_ceo_owner_name = supplier.company_ceo_owner_name
            supplier_instance.company_ceo_owner_email = supplier.company_ceo_owner_email
            supplier_instance.company_number_of_employee_id = supplier.company_number_of_employee
            supplier_instance.company_website = supplier.company_website
            supplier_instance.company_tag_line = supplier.company_tag_line
            supplier_instance.company_description = supplier.company_description
            supplier_instance.company_established_since = supplier.company_established_since
            supplier_instance.company_anniversary_date = supplier.company_anniversary_date
            supplier_instance.gender_id = supplier.gender
            supplier_instance.phone = supplier.phone
            supplier_instance.position_id = supplier.position
            supplier_instance.picture = picture
            supplier_instance.language_id = supplier.language
            supplier_instance.currency_id = supplier.currency
            supplier_instance.bank_name = supplier.bank_name
            supplier_instance.bank_code = supplier.bank_code
            supplier_instance.bank_address = supplier.bank_address
            supplier_instance.beneficiary_name = supplier.beneficiary_name
            supplier_instance.switch_bic_code = supplier.switch_bic_code
            supplier_instance.bank_currency_id = supplier.bank_currency
            supplier_instance.bank_account_number = supplier.bank_account_number
            supplier_instance.international_bank = supplier.international_bank
            supplier_instance.profile_features_id = profile_features
            supplier_instance.sicp_registration_id = sicp_registration
            supplier_instance.promotion_id = promotion

            supplier_instance.save()
            supplier_instance.user.last_name = user.last_name
            supplier_instance.user.first_name = user.first_name
            if supplier.is_delete.company_credential_profiles:
                SupplierCompanyCredential.objects.filter(supplier_id=supplier_instance.id).delete()
                for company_credential in supplier.company_credential_profiles:
                    company_credential_instance = SupplierCompanyCredential(supplier=supplier_instance, company_credential_profile=company_credential)
                    company_credential_instance.save()

            if supplier.is_delete.supplier_form_registrations:
                SupplierFormRegistrations.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_form_registration in supplier.supplier_form_registrations:
                    form_registration_instance = SupplierFormRegistrations(supplier=supplier_instance, form_registration=supplier_form_registration)
                    form_registration_instance.save()

            if supplier.is_delete.bank_certifications:
                SupplierBankCertification.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_bank_certification in supplier.bank_certifications:
                    bank_certification_instance = SupplierBankCertification(
                        supplier=supplier_instance, bank_certification=supplier_bank_certification
                    )
                    bank_certification_instance.save()

            if supplier.is_delete.quality_certifications:
                SupplierQualityCertification.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_quality_certification in supplier.quality_certifications:
                    quality_certification_instance = SupplierQualityCertification(
                        supplier=supplier_instance, quality_certification=supplier_quality_certification
                    )
                    quality_certification_instance.save()

            if supplier.is_delete.business_licenses:
                SupplierBusinessLicense.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_business_license in supplier.business_licenses:
                    business_license_instance = SupplierBusinessLicense(supplier=supplier_instance, business_license=supplier_business_license)
                    business_license_instance.save()

            if supplier.is_delete.tax_certifications:
                SupplierTaxCertification.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_tax_certification in supplier.tax_certifications:
                    tax_certification_instance = SupplierTaxCertification(supplier=supplier_instance, tax_certification=supplier_tax_certification)
                    tax_certification_instance.save()

            if supplier.is_delete.others:
                SupplierOthers.objects.filter(supplier_id=supplier_instance.id).delete()
                for supplier_other in supplier.others:
                    other_instance = SupplierOthers(supplier=supplier_instance, other=supplier_other)
                    other_instance.save()

            percentage_category = 0
            for categories in supplier.core_business:
                if len(categories) > 10:
                    raise GraphQLError("Number category  is less than or equals 10")
                for category in categories:
                    percentage_category += category.percentage
            if percentage_category != 100:
                raise GraphQLError("Total percentage core business must be equals 100")
            for categories in supplier.core_business:
                for category in categories:
                    category_mapping = SupplierCategory.objects.filter(
                        user_supplier_id=supplier_instance.id, category_id=category.category
                    )
                    if category_mapping.exists():
                        category_mapping = category_mapping.first()
                        category_mapping.percentage = category.percentage
                        category_mapping.minimum_of_value = category.minimum_of_value
                        category_mapping.save()
                        pass
                    else:
                        category_instance = SupplierCategory(
                            percentage=category.percentage,
                            minimum_of_value=category.minimum_of_value,
                            user_supplier_id=supplier_instance.id,
                            category_id=category.category,
                        )
                        category_instance.save()

            if len(supplier.industries) > 10:
                raise GraphQLError("Number industry  is less than or equals 10")

            percentage_industry = 0
            for industry in supplier.industries:
                percentage_industry += industry.percentage

            percentage_client_focus = 0
            for client_focus in supplier.client_focus:
                percentage_client_focus += client_focus.percentage

            if percentage_client_focus != 100 or percentage_industry != 100:
                raise GraphQLError("Total percentage must be equals 100")

            for industry in supplier.industries:
                industry_mapping = SupplierIndustry.objects.filter(
                    industry_sub_sectors_id=industry.industry_sub_sectors, user_supplier_id=supplier_instance.id
                )
                if industry_mapping.exists():
                    industry_mapping = industry_mapping.first()
                    industry_mapping.percentage = industry.percentage
                    industry_mapping.save()
                else:
                    industry_instance = SupplierIndustry(
                        percentage=industry.percentage,
                        industry_sub_sectors_id=industry.industry_sub_sectors,
                        user_supplier_id=supplier_instance.id,
                    )
                    industry_instance.save()

            for client_focus in supplier.client_focus:
                client_focus_mapping = SupplierClientFocus.objects.filter(
                    client_focus_id=client_focus.client_focus, user_supplier_id=supplier_instance.id
                )
                if client_focus_mapping.exists():
                    client_focus_mapping = client_focus_mapping.first()
                    client_focus_mapping.percentage = client_focus.percentage
                    client_focus_mapping.save()
                else:
                    client_focus_intance = SupplierClientFocus(
                        percentage=client_focus.percentage,
                        client_focus_id=client_focus.client_focus,
                        user_supplier_id=supplier_instance.id,
                    )
                    client_focus_intance.save()

            # delete category
            list_category_mapping = map(
                lambda x: int(x.get('category_id')), SupplierCategory.objects.filter(user_supplier_id=supplier_instance.id).values('category_id')
            )
            list_category_mapping = set(list_category_mapping)
            list_category = []
            for categories in supplier.core_business:
                for category in categories:
                    list_category.append(int(category.category))
            list_category = set(list_category)
            list_delete = list_category_mapping.difference(list_category)
            SupplierCategory.objects.filter(user_supplier_id=supplier_instance.id, category_id__in=list_delete).delete()

            #  delete industry
            list_industry_mapping = map(
                lambda x: x.get('industry_sub_sectors_id'),
                SupplierIndustry.objects.filter(user_supplier_id=supplier_instance.id).values('industry_sub_sectors_id'),
            )
            list_industry_mapping = set(list_industry_mapping)
            list_industry = []
            for industry in supplier.industries:
                list_industry.append(int(industry.industry_sub_sectors))
            list_industry = set(list_industry)
            list_delete = list_industry_mapping.difference(list_industry)
            SupplierIndustry.objects.filter(user_supplier_id=supplier_instance.id, industry_sub_sectors_id__in=list_delete).delete()

            #  delete client focus
            list_client_focus_mapping = map(
                lambda x: x.get('client_focus_id'),
                SupplierClientFocus.objects.filter(user_supplier_id=supplier_instance.id).values('client_focus_id'),
            )
            list_client_focus_mapping = set(list_client_focus_mapping)
            list_client_focus = []
            for client_focus in supplier.client_focus:
                list_client_focus.append(int(client_focus.client_focus))
            list_client_focus = set(list_client_focus)
            list_delete = list_client_focus_mapping.difference(list_client_focus)
            SupplierClientFocus.objects.filter(user_supplier_id=supplier_instance.id, client_focus_id__in=list_delete).delete()

            # portfolio
            for portfolio_delete in supplier.portfolios_delete:
                SupplierPortfolio.objects.get(id=portfolio_delete).delete()

            for portfolio in supplier.portfolios:
                if portfolio.id is not None:
                    portfolio_mapping = SupplierPortfolio.objects.get(id=portfolio.id)
                    portfolio_mapping.company = portfolio.company
                    portfolio_mapping.project_name = portfolio.project_name
                    portfolio_mapping.value = portfolio.value
                    portfolio_mapping.project_description = portfolio.project_description
                    if portfolio.image is None and not portfolio.is_delete_image:
                        image = portfolio_mapping.image
                    else:
                        image = portfolio.image
                    portfolio_mapping.image = image
                    portfolio_mapping.save()
                else:
                    portfolio_instance = SupplierPortfolio(
                        company=portfolio.company,
                        project_name=portfolio.project_name,
                        value=portfolio.value,
                        project_description=portfolio.project_description,
                        image=portfolio.image,
                        user_supplier_id=supplier_instance.id,
                    )
                    portfolio_instance.save()

            return SupplierProfileUpdate(status=True, supplier=supplier_instance)
        except Exception as errors:
            transaction.set_rollback(True)
            return SupplierProfileUpdate(errors)


class SupplierStatusUpdateInput(graphene.InputObjectType):
    supplier_id = graphene.String(required=True)
    status = graphene.Int(required=True)


class SupplierStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        reason_manual = graphene.String()
        list_status = graphene.List(SupplierStatusUpdateInput, required=True)

    def mutate(root, info, list_status, reason_manual=None):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            for supplier_status in list_status:
                supplier = Supplier.objects.select_related('user').get(pk=supplier_status.supplier_id)
                supplier.user.status = supplier_status.status
                supplier.user.save()
                supplier_activity = SupplierActivity(
                    supplier=supplier, changed_by_id=token.user.id, reason_manual=reason_manual, changed_state=supplier_status.status
                )
                supplier_activity.save()
            return SupplierStatusUpdate(status=True)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
            return SupplierStatusUpdate(status=False, error=error)

class SupplierEmailUpdateInput(graphene.InputObjectType):
    supplier_id = graphene.String(required=True)
    email = graphene.String(required=True)


class SupplierEmailUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    supplier = graphene.Field(SupplierNode)

    class Arguments:
        input = SupplierEmailUpdateInput(required=True)

    def mutate(root, info, input):
        token = GetToken.getToken(info)
        if token.user.isSupplier():
            supplier_instance = Supplier.objects.filter(id=input.supplier_id).first()
            user = User.objects.filter(id=supplier_instance.user_id).first()
            user.email = input.email
            user.save()            
            return SupplierEmailUpdate(status=True, supplier=supplier_instance)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
            return SupplierEmailUpdate(status=False, error=error)

# -------------Admin------------------
class GroupNode(DjangoObjectType):
    class Meta:
        model = Group
        filter_fields = ['id']
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection


class GroupCreate(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    status = graphene.Boolean()
    group = graphene.Field(GroupNode)

    def mutate(root, info, name):
        group = Group(name=name)
        group.save()
        return GroupCreate(status=True, group=group)

class GroupDelete(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    status = graphene.Boolean()

    def mutate(root, info, id):
        group = Group(id=id)
        group.delete()
        return GroupDelete(status=True)


class GroupPermissionNode(DjangoObjectType):
    class Meta:
        model = GroupPermission
        filter_fields = ['id']
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection


class GroupPermissionCreate(graphene.Mutation):
    class Arguments:
        group = graphene.String(required=True)
        role = graphene.Int(required=True)

    status = graphene.Boolean()

    def mutate(root, info, group, role):
        group_permission = GroupPermission(group_id=group, role=role)
        group_permission.save()
        return GroupPermissionCreate(status=True)


class UserPermissionFilter(FilterSet):
    created = django_filters.CharFilter(method='created_filter')
    username = django_filters.CharFilter(method='username_filter')
    email = django_filters.CharFilter(method='email_filter')
    status = django_filters.CharFilter(method='status_filter')
    short_name = django_filters.CharFilter(method='short_name_filter')
    valid_from = django_filters.CharFilter(method='valid_from_filter')
    valid_to = django_filters.CharFilter(method='valid_to_filter')
    role = django_filters.CharFilter(method='role_filter')
    modules = django_filters.CharFilter(method='modules_filter')
    email_substitution = django_filters.CharFilter(method='email_substitution_filter')
    short_name_substitution = django_filters.CharFilter(method='short_name_substitution_filter')

    class Meta:
        model = UsersPermission
        fields = [
            'id',
            'status',
        ]

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('permission__role', 'role'),
            ('permission__group', 'modules'),
            ('valid_from', 'valid_from'),
            ('valid_to', 'valid_to'),
            ('user__email', 'email'),
            ('user__created', 'created'),
            ('status', 'status'),
            ('user__username', 'username'),
            ('user__short_name', 'short_name'),
        )
    )

    def email_filter(self, queryset, name, value):
        queryset = queryset.filter(user__email__icontains=value)
        return queryset

    def username_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username__icontains=value)
        return queryset

    def status_filter(self, queryset, name, value):
        queryset = queryset.filter(status=value)
        return queryset

    def created_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(user__created__range=(value, value_to))
        return queryset

    def short_name_filter(self, queryset, name, value):
        queryset = queryset.filter(user__short_name__icontains=value)
        return queryset

    def valid_from_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(valid_from__date__gte=value)
        return queryset

    def valid_to_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(valid_to__date__lte=value)
        return queryset

    def role_filter(self, queryset, name, value):
        queryset = queryset.filter(permission__role=value)
        return queryset

    def modules_filter(self, queryset, name, value):
        queryset = queryset.filter(permission__group=value)
        return queryset

    def email_substitution_filter(self, queryset, name, value):
        list_user_id = map(lambda x: x.get('id'), User.objects.filter(email__icontains=value).values('id'))
        list_id = map(
            lambda x: x.get('user_permission_id'), UserSubstitutionPermission.objects.filter(user_id__in=list_user_id).values('user_permission_id')
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def short_name_substitution_filter(self, queryset, name, value):
        list_user_id = map(lambda x: x.get('id'), User.objects.filter(short_name__icontains=value).values('id'))
        list_id = map(
            lambda x: x.get('user_permission_id'), UserSubstitutionPermission.objects.filter(user_id__in=list_user_id).values('user_permission_id')
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

class UsersPermissionNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = UsersPermission
        filterset_class = UserPermissionFilter
        interfaces = (CustomNode,)
        convert_choices_to_enum = False
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = queryset.filter().order_by('id')
        return queryset

class AdminFilter(FilterSet):
    created = django_filters.CharFilter(method='created_filter')
    username = django_filters.CharFilter(method='username_filter')
    email = django_filters.CharFilter(method='email_filter')
    status = django_filters.CharFilter(method='status_filter')
    short_name = django_filters.CharFilter(method='short_name_filter')
    valid_from = django_filters.CharFilter(method='valid_from_filter')
    valid_to = django_filters.CharFilter(method='valid_to_filter')
    long_name = django_filters.CharFilter(lookup_expr='contains')
<<<<<<< Updated upstream
    role=django_filters.CharFilter(method='role_filter')
=======
    chuyen_nganh = django_filters.CharFilter(lookup_expr='icontains')  # Thêm bộ lọc cho chuyen_nganh
>>>>>>> Stashed changes

    class Meta:
        model = Admin
        fields = ['id', 'long_name', 'chuyen_nganh']  # Thêm chuyen_nganh vào fields

    order_by = OrderingFilter(
            fields=(
            ('id', 'id'),
            ('role', 'role'),
            ('long_name', 'long_name'),
            ('user__email', 'email'),
            ('user__created', 'created'),
            ('user__status', 'status'),
            ('user__username', 'username'),
            ('user__short_name', 'short_name'),
            ('chuyen_nganh', 'chuyen_nganh'),  # Cho phép sắp xếp theo chuyen_nganh
        )
    )

    def email_filter(self, queryset, name, value):
        return queryset.filter(user__email=value)

    def role_filter(self, queryset, name, value):
        queryset = queryset.filter(user__role=value)
        return queryset

    def username_filter(self, queryset, name, value):
        return queryset.filter(user__username=value)

    def status_filter(self, queryset, name, value):
        return queryset.filter(user__status=value)

    def created_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        return queryset.filter(user__created__range=(value, value_to))

    def short_name_filter(self, queryset, name, value):
        return queryset.filter(user__short_name__contains=value)

class AdminNode(DjangoObjectType):
    language = graphene.Field(LanguageNode)
    chuyen_nganh = graphene.String()  # Thêm chuyen_nganh vào node

    class Meta:
        model = Admin
        filterset_class = AdminFilter
        interfaces = (CustomNode, UserInterface)
        connection_class = ExtendedConnection

<<<<<<< Updated upstream
=======
    def resolve_picture(self, info):
        if self.picture and hasattr(self.picture, 'url'):
            return info.context.build_absolute_uri(self.picture.url)
        return ''

>>>>>>> Stashed changes
    def resolve_language(self, info):
        return self.user.language

    def resolve_chuyen_nganh(self, info):
        return self.chuyen_nganh  # Trả về giá trị chuyen_nganh

class PermissionInput(graphene.InputObjectType):
    valid_from = graphene.String(required=True)
    valid_to = graphene.String(required=True)
    role = graphene.Int(required=True)
    modules = graphene.String(required=True)

class UserAdminInput(graphene.InputObjectType):
    password = graphene.String(required=True)
    email = graphene.String(required=True)
    short_name = graphene.String(required=True)
    status = graphene.Int()

class AdminInput(graphene.InputObjectType):
    user = UserInput(required=True)
    long_name = graphene.String(required=True)
<<<<<<< Updated upstream
    role = graphene.Int(required=True)
=======
    role = graphene.Int(required=True)  # Thêm trường role để xác định vai trò
    chuyen_nganh = graphene.String()  # Thêm chuyen_nganh


>>>>>>> Stashed changes

class UserAdminUpdateInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    short_name = graphene.String(required=True)
    status = graphene.Int()

class AdminUpdateInput(graphene.InputObjectType):
    user = graphene.Field(UserAdminUpdateInput, required=True)
    long_name = graphene.String(required=True)
    role = graphene.Int(required=True)  # Thêm trường role để xác định vai trò
    chuyen_nganh = graphene.String()  # Thêm chuyen_nganh

class AdminProfileUpdateInput(graphene.InputObjectType):
    user = graphene.Field(UserAdminUpdateInput, required=True)
    long_name = graphene.String(required=True)
    picture = Upload()

class AdminCreate(graphene.Mutation):
    class Arguments:
        admin = AdminInput(required=True)

    status = graphene.Boolean()
    admin = graphene.Field(AdminNode)
    error = graphene.Field(Error)

    def mutate(root, info, admin=None):
<<<<<<< Updated upstream
        # Bỏ qua kiểm tra quyền để test
        # if checkPermission(info):

        # Kiểm tra nếu email đã tồn tại
        if User.objects.filter(user_type=1, email=admin.user.email).exists():
            error = Error(code="USER_01", message=UserError.USER_01)
=======
        if checkPermission(info):
            current_admin = Admin.objects.get(user=info.context.user)
            if current_admin.role != 1:
                error = Error(code="USER_03", message="Bạn không có quyền tạo tài khoản.")
                return AdminCreate(status=False, error=error)

            if User.objects.filter(user_type=1, email=admin.user.email).exists():
                error = Error(code="USER_01", message=UserError.USER_01)
                return AdminCreate(status=False, error=error)

            last_created_admin = User.objects.filter(user_type=1).order_by("-username").first()
            last_user_id_str = last_created_admin.username[2:]
            user_count = int(last_user_id_str) + 1
            username = '70' + str(user_count).zfill(4)
            user = User(username=username, user_type=1, **admin.user)
            user.set_password(admin.user.password)
            user.save()
            
            admin_instance = Admin(
                long_name=admin.long_name,
                user=user,
                role=admin.role,
                chuyen_nganh=admin.chuyen_nganh  # Gán chuyen_nganh
            )
            admin_instance.save()

            return AdminCreate(status=True, admin=admin_instance)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
>>>>>>> Stashed changes
            return AdminCreate(status=False, error=error)

        # Tạo User và Admin mới
        last_created_admin = User.objects.filter(user_type=1).order_by("-username").first()

        if last_created_admin:
            last_user_id_str = last_created_admin.username[2:]
            user_count = int(last_user_id_str) + 1
        else:
            user_count = 1

        username = '70' + str(user_count).zfill(4)
        user = User(username=username, user_type=1, **admin.user)
        user.set_password(admin.user.password)
        user.save()

        admin_instance = Admin(long_name=admin.long_name, user=user, role=admin.role)
        admin_instance.save()

        return AdminCreate(status=True, admin=admin_instance)
        # else:
        #     error = Error(code="USER_02", message=UserError.USER_02)
        #     return AdminCreate(status=False, error=error)


class AdminUpdate(graphene.Mutation):
    class Arguments:
        is_delete = graphene.Boolean(required=True)
        id = graphene.String(required=True)
        admin = AdminUpdateInput(required=True)

    status = graphene.Boolean()
    admin = graphene.Field(AdminNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, is_delete, admin=None):
        if checkPermission(info):
            admin_instance = Admin.objects.get(pk=id)
            user = User.objects.get(pk=admin_instance.user_id)
            user.short_name = admin.user.short_name
            user.status = admin.user.status

            if admin.picture is None and not is_delete:
                picture = admin_instance.picture
            else:
                picture = admin.picture

            admin_instance.long_name = admin.long_name
            admin_instance.picture = picture
            admin_instance.chuyen_nganh = admin.chuyen_nganh  # Cập nhật chuyen_nganh nếu có
            time_now = timezone.now()

            for permission in admin.permissions:
                valid_from1 = datetime.strptime(permission.valid_from, '%Y-%m-%dT%H:%M:%S%z')
                status_input = 4
                value_form_check = valid_from1 + timezone.timedelta(days=1)
                if valid_from1 <= time_now < value_form_check:
                    status_input = 1
                valid_to1 = datetime.strptime(permission.valid_to, '%Y-%m-%dT%H:%M:%S%z')
                group_permission = GroupPermission.objects.filter(group_id=permission.modules, role=permission.role).first()
                user_permission_mapping = UsersPermission.objects.filter(permission_id=group_permission.id, status__in=[1, 4])

                for user_permission in user_permission_mapping:
                    valid_from = user_permission.valid_from
                    valid_to = user_permission.valid_to
                    if valid_from <= valid_from1 <= valid_to:
                        error = Error(code="USER_07", message=UserError.USER_07)
                        return AdminUpdate(status=False, error=error)
                    if valid_from <= valid_to1 <= valid_to:
                        error = Error(code="USER_07", message=UserError.USER_07)
                        return AdminUpdate(status=False, error=error)
                    if valid_from >= valid_from1 and valid_to <= valid_to1:
                        error = Error(code="USER_07", message=UserError.USER_07)
                        return AdminUpdate(status=False, error=error)
                        
                user_permission = UsersPermission(
                    permission_id=group_permission.id,
                    valid_from=permission.valid_from,
                    valid_to=permission.valid_to,
                    user=user,
                    status=status_input
                )
                user_permission.save()

            admin_instance.save()
            user.save()
            return AdminUpdate(status=True, admin=admin_instance)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
            return AdminUpdate(status=False, error=error)


class AdminDelete(graphene.Mutation):
    status = graphene.Boolean()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id):
        admin = Admin.objects.select_related('user').get(pk=id)
        admin.user.delete()
        return AdminDelete(status=True)

class AdminProfileUpdate(graphene.Mutation):
    class Arguments:
        is_delete = graphene.Boolean(required=True)
        id = graphene.String(required=True)
        admin = AdminProfileUpdateInput(required=True)

    status = graphene.Boolean()
    admin = graphene.Field(AdminNode)

    def mutate(root, info, id, is_delete, admin=None):
        admin_intance = Admin.objects.get(pk=id)
        user = User.objects.get(pk=admin_intance.user_id)
        user.short_name = admin.user.short_name
        user.status = admin.user.status
        if admin.picture is None and not is_delete:
            picture = admin_intance.picture
        else:
            picture = admin.picture
        admin_intance.long_name = admin.long_name
        admin_intance.picture = picture
        admin_intance.save()
        user.save()
        return AdminProfileUpdate(status=True, admin=admin_intance)

class AdminStatusUpdateInput(graphene.InputObjectType):
    admin_id = graphene.String(required=True)
    status = graphene.Int(required=True)

class AdminStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(AdminStatusUpdateInput, required=True)

    def mutate(root, info, list_status):
        if checkPermission(info):
            for admin_status in list_status:
                admin = Admin.objects.select_related('user').get(pk=admin_status.admin_id)
                admin.user.status = admin_status.status
                admin.user.save()
            return AdminStatusUpdate(status=True)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
            return AdminStatusUpdate(status=False, error=error)

class UsersPermissionUpdateStatusInput(graphene.InputObjectType):
    users_permission_id = graphene.String(required=True)
    status = graphene.Int(required=True)

class UsersPermissionUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(UsersPermissionUpdateStatusInput, required=True)

    def mutate(root, info, list_status):
        if checkPermission(info):
            for permission in list_status:
                user_permission = UsersPermission.objects.get(pk=permission.users_permission_id)
                user_permission.status = permission.status
                user_permission.save()
                user_substitution_permissions = UserSubstitutionPermission.objects.filter(user_permission_id=user_permission.id)
                for user_substitution_permission in user_substitution_permissions:
                    user_substitution_permission.status = permission.status
                    user_substitution_permission.save()
            return UsersPermissionUpdateStatus(status=True)
        else:
            error = Error(code="USER_02", message=UserError.USER_02)
            return UsersPermissionUpdateStatus(status=False, error=error)

class UserSubstitutionPermissionNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = UserSubstitutionPermission
        filter_fields = ['id']
        interfaces = (CustomNode,)
        convert_choices_to_enum = False
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = queryset.filter().order_by('id')
        return queryset

class UserSubstitutionPermissionInput(graphene.InputObjectType):
    user_permission_id = graphene.String(required=True)
    valid_from = graphene.String(required=True)
    valid_to = graphene.String(required=True)
    user_id = graphene.String(required=True)

class UserSubstitutionPermissionCreate(graphene.Mutation):
    class Arguments:
        user_substitution_permission = UserSubstitutionPermissionInput(required=True)

    status = graphene.Boolean()
    user_substitution_permission = graphene.Field(UserSubstitutionPermissionNode)
    error = graphene.Field(Error)

    def mutate(root, info, user_substitution_permission=None):
        user_permission_id = user_substitution_permission.user_permission_id
        user_id = user_substitution_permission.user_id
        valid_from_input = datetime.strptime(user_substitution_permission.valid_from, '%Y-%m-%dT%H:%M:%S%z')
        valid_to_input = datetime.strptime(user_substitution_permission.valid_to, '%Y-%m-%dT%H:%M:%S%z')
        user_permission = UsersPermission.objects.get(id=user_permission_id, status__in=[1, 4])
        valid_from = user_permission.valid_from
        valid_to = user_permission.valid_to
        time_now = timezone.now()
        status_input = 4
        value_form_check = valid_from_input + timezone.timedelta(days=1)
        if valid_from_input <= time_now < value_form_check:
            status_input = 1
        if valid_from_input < valid_from or valid_to < valid_to_input:
            error = Error(code="USER_07", message=UserError.USER_07)
            return UserSubstitutionPermissionCreate(status=False, error=error)
        user_substitution_permission_mapping = UserSubstitutionPermission.objects.filter(user_permission_id=user_permission_id, status__in=[1, 4])
        for user_substitution_permission in user_substitution_permission_mapping:
            valid_from = user_substitution_permission.valid_from
            valid_to = user_substitution_permission.valid_to
            if valid_from <= valid_from_input <= valid_to:
                error = Error(code="USER_07", message=UserError.USER_07)
                return UserSubstitutionPermissionCreate(status=False, error=error)
            if valid_from <= valid_to_input <= valid_to:
                error = Error(code="USER_07", message=UserError.USER_07)
                return UserSubstitutionPermissionCreate(status=False, error=error)
            if valid_from >= valid_from_input and valid_to <= valid_to_input:
                error = Error(code="USER_07", message=UserError.USER_07)
                return UserSubstitutionPermissionCreate(status=False, error=error)
        user_substitution_permission = UserSubstitutionPermission(
            user_permission_id=user_permission_id, valid_from=valid_from_input, valid_to=valid_to_input, user_id=user_id, status=status_input
        )
        user_substitution_permission.save()
        return UserSubstitutionPermissionCreate(status=True, user_substitution_permission=user_substitution_permission)

class UserSubstitutionPermissionUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        user_substitution_permission = UserSubstitutionPermissionInput(required=True)

    status = graphene.Boolean()
    user_substitution_permission = graphene.Field(UserSubstitutionPermissionNode)
    error = graphene.Field(Error)

    def mutate(root, info, user_substitution_permission, id):
        user_permission_id = user_substitution_permission.user_permission_id
        user_id = user_substitution_permission.user_id
        valid_from_input = datetime.strptime(user_substitution_permission.valid_from, '%Y-%m-%dT%H:%M:%S%z')
        valid_to_input = datetime.strptime(user_substitution_permission.valid_to, '%Y-%m-%dT%H:%M:%S%z')
        user_permission = UsersPermission.objects.get(id=user_permission_id, status__in=[1, 4])
        valid_from = user_permission.valid_from
        valid_to = user_permission.valid_to
        time_now = timezone.now()
        status_input = 4
        value_form_check = valid_from_input + timezone.timedelta(days=1)
        if valid_from_input <= time_now < value_form_check:
            status_input = 1
        if valid_from_input < valid_from or valid_to < valid_to_input:
            error = Error(code="USER_07", message=UserError.USER_07)
            return UserSubstitutionPermissionUpdate(status=False, error=error)
        user_substitution_permission_mapping = UserSubstitutionPermission.objects.filter(
            user_permission_id=user_permission_id, status__in=[1, 4]
        ).exclude(id=id)
        for user_substitution_permission in user_substitution_permission_mapping:
            valid_from = user_substitution_permission.valid_from
            valid_to = user_substitution_permission.valid_to
            if valid_from <= valid_from_input <= valid_to:
                error = Error(code="USER_07", message=UserError.USER_07)
                return UserSubstitutionPermissionUpdate(status=False, error=error)
            if valid_from <= valid_to_input <= valid_to:
                error = Error(code="USER_07", message=UserError.USER_07)
                return UserSubstitutionPermissionUpdate(status=False, error=error)
            if valid_from >= valid_from_input and valid_to <= valid_to_input:
                error = Error(code="USER_07", message=UserError.USER_07)
                return UserSubstitutionPermissionUpdate(status=False, error=error)
        user_substitution_permission = UserSubstitutionPermission.objects.get(id=id)
        user_substitution_permission.user_permission_id = user_permission_id
        user_substitution_permission.valid_from = valid_from_input
        user_substitution_permission.valid_to = valid_to_input
        user_substitution_permission.user_id = user_id
        user_substitution_permission.status = status_input
        user_substitution_permission.save()
        return UserSubstitutionPermissionUpdate(status=True, user_substitution_permission=user_substitution_permission)

class UserSubstitutionPermissionUpdateStatusInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    status = graphene.Int(required=True)

class UserSubstitutionPermissionUpdateStatus(graphene.Mutation):
    class Arguments:
        list_substitution = graphene.List(UserSubstitutionPermissionUpdateStatusInput, required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, list_substitution):
        token = GetToken.getToken(info)
        for substitution_permission in list_substitution:
            user_substitution_permission = UserSubstitutionPermission.objects.get(id=substitution_permission.id)
            if token.user.id == user_substitution_permission.user_permission.user_id or checkPermission(info):
                user_substitution_permission.status = substitution_permission.status
                user_substitution_permission.save()
            else:
                error = Error(code="USER_02", message=UserError.USER_02)
                return UserSubstitutionPermissionUpdateStatus(status=False, error=error)
        return UserSubstitutionPermissionUpdateStatus(status=True)

def checkPermission(info):
    token = GetToken.getToken(info)
    user = User.objects.select_related('admin').get(id=token.user.id)
    list_group_permission_id = map(lambda x: x.get('id'), GroupPermission.objects.filter(role=1).values('id'))
    user_permissions = UsersPermission.objects.filter(permission_id__in=list_group_permission_id, status=1, user_id=user.id)
    if user_permissions.exists():
        return True
    else:
        return False

class SupplierProfileCompanyUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)

    class Meta:
        model = Supplier
        exclude_fields = ['id', 'user', 'profile_features', 'valid_from', 'valid_to', 'sicp_registration']
        allow_unauthenticated = True

    @classmethod
    def mutate(cls, root, info, input):
        return super().mutate(root, info, input)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        payload = super().perform_mutation(root, info, **data)
        return SupplierProfileCompanyUpdate(status=True, supplier=payload.supplier)

class BuyerProfileCompanyUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)

    class Meta:
        model = Buyer
        exclude_fields = ['id', 'user', 'profile_features', 'valid_from', 'valid_to']
        allow_unauthenticated = True

    @classmethod
    def mutate(cls, root, info, input):
        user = GetToken.getToken(info).user.buyer
        return super().mutate(root, info, input)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        payload = super().perform_mutation(root, info, **data)
        return BuyerProfileCompanyUpdate(status=True, buyer=payload.buyer)

# -------------------------supplier sub account--------------------------
class SupplierSubAccountActivityFilter(FilterSet):
    changed_by = django_filters.CharFilter(method='changed_by_filter')
    changed_date = django_filters.CharFilter(method='changed_date_filter')
    reason_manual = django_filters.CharFilter(method='reason_manual_filter')
    changed_state = django_filters.CharFilter(method='changed_state_filter')

    class Meta:
        model = SupplierSubAccount
        fields = ['id']

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('changed_by__username', 'changed_by'),
            ('changed_date', 'changed_date'),
            ('reason_manual', 'reason_manual'),
            ('changed_state', 'changed_state'),
        )
    )

    def changed_by_filter(self, queryset, name, value):
        queryset = queryset.filter(changed_by__username__icontains=value)
        return queryset

    def changed_date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(changed_date__range=(value, value_to))
        return queryset

    def reason_manual_filter(self, queryset, name, value):
        queryset = queryset.filter(reason_manual__icontains=value)
        return queryset

    def changed_state_filter(self, queryset, name, value):
        queryset = queryset.filter(changed_state=value)
        return queryset


class SupplierSubAccountActivityNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = SupplierSubAccountActivity
        interfaces = (CustomNode,)
        convert_choices_to_enum = False
        filterset_class = SupplierSubAccountActivityFilter
        connection_class = ExtendedConnection


class SupplierSubAccountFilter(FilterSet):
    created = django_filters.CharFilter(method='created_filter')
    username = django_filters.CharFilter(method='username_filter')
    email = django_filters.CharFilter(method='email_filter')
    status = django_filters.CharFilter(method='status_filter')
    valid_from = django_filters.CharFilter(method='valid_from_filter')
    valid_to = django_filters.CharFilter(method='valid_to_filter')
    changed_by = django_filters.CharFilter(method='changed_by_filter')
    changed_date = django_filters.CharFilter(method='changed_date_filter')
    reason_manual = django_filters.CharFilter(method='reason_manual_filter')
    changed_state = django_filters.CharFilter(method='changed_state_filter')
    profile_feature = django_filters.CharFilter(method='profile_feature_filter')
    flash_sale = django_filters.NumberFilter(method='flash_sale_filter')
    report_year = django_filters.NumberFilter(method='report_year_filter')
    supplier_id = django_filters.CharFilter(method='supplier_filter')

    class Meta:
        model = SupplierSubAccount
        fields = {
            'id': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('user__email', 'email'),
            ('user__created', 'created'),
            ('user__status', 'status'),
            ('user__username', 'username'),
            ('user__full_name', 'full_name'),
            ('supplier__profile_features__name', 'profile_features'),
            ('supplier__profile_features__flash_sale', 'flash_sale'),
            ('supplier__profile_features__report_year', 'report_year'),
            ('supplier__valid_from', 'valid_from'),
            ('supplier__valid_to', 'valid_to'),
        )
    )

    def email_filter(self, queryset, name, value):
        queryset = queryset.filter(user__email__icontains=value)
        return queryset

    def username_filter(self, queryset, name, value):
        queryset = queryset.filter(user__username__icontains=value)
        return queryset

    def status_filter(self, queryset, name, value):
        queryset = queryset.filter(user__status=value)
        return queryset

    def created_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(user__created__range=(value, value_to))
        return queryset

    def valid_from_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(supplier__valid_from__gte=value)
        return queryset

    def valid_to_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(supplier__valid_to__lte=value)
        return queryset

    def changed_by_filter(self, queryset, name, value):
        list_system = []
        list_user_id = map(lambda x: x.get('id'), User.objects.filter(username__icontains=value).values('id'))
        list_id = map(
            lambda x: x.get('supplier_sub_account_id'),
            SupplierSubAccountActivity.objects.filter(changed_by_id__in=list_user_id).values('supplier_sub_account_id'),
        )
        if value in "system":
            list_system = map(lambda x: x.get('supplier_id'), SupplierActivity.objects.filter(changed_by_id=None).values('supplier_id'))
        list_id = list(list_id) + list(list_system)
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        list_id = map(
            lambda x: x.get('supplier_sub_account_id'),
            SupplierSubAccountActivity.objects.filter(changed_date__range=(value, value_to)).values('supplier_sub_account_id'),
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def reason_manual_filter(self, queryset, name, value):
        list_id = map(
            lambda x: x.get('supplier_sub_account_id'),
            SupplierSubAccountActivity.objects.filter(reason_manual__icontains=value).values('supplier_sub_account_id'),
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def changed_state_filter(self, queryset, name, value):
        list_id = map(
            lambda x: x.get('supplier_sub_account_id'),
            SupplierSubAccountActivity.objects.filter(changed_state=value).values('supplier_sub_account_id'),
        )
        queryset = queryset.filter(id__in=list_id)
        return queryset

    def profile_feature_filter(self, queryset, name, value):
        queryset = queryset.filter(supplier__profile_features_id=value)
        return queryset

    def flash_sale_filter(self, queryset, name, value):
        queryset = queryset.filter(supplier__profile_features__flash_sale=value)
        return queryset

    def report_year_filter(self, queryset, name, value):
        queryset = queryset.filter(supplier__profile_features__report_year=value)
        return queryset
    
    def supplier_filter(self, queryset, name, value):
        queryset = queryset.filter(supplier__id=value)
        return queryset


class SupplierSubAccountNode(DjangoObjectType):
    class Meta:
        model = SupplierSubAccount
        interfaces = (CustomNode, UserInterface)
        convert_choices_to_enum = False
        filterset_class = SupplierSubAccountFilter
        connection_class = ExtendedConnection

    def resolve_picture(self, info):
        if self.picture and hasattr(self.picture, 'url'):
            return info.context.build_absolute_uri(self.picture.url)
        else:
            return ''

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


class UserDiamondSponsorFilter(FilterSet):
    valid_from = django_filters.DateFilter(field_name="valid_from", lookup_expr="date__gte")
    valid_to = django_filters.DateFilter(field_name="valid_to", lookup_expr="date__lte")
    company_name_filter = django_filters.CharFilter(method="filter_company_name")
    search_ccc_filter = django_filters.CharFilter(method="filter_search_ccc")
    exclude_id_list = django_filters.CharFilter(method="exclude_by_id_list")

    class Meta:
        model = UserDiamondSponsor
        fields = {
            'id': ['exact'],
            'description': ['icontains'],
            'status': ['exact'],
            'is_active': ['exact'],
            'is_confirmed': ['exact'],
        }

    order_by = OrderingFilter(fields=('id', 'description', 'status', 'is_active', 'is_confirmed', 'valid_from', 'valid_to'))

    def filter_search_ccc(self, queryset, name, value):
        supplier_ids = []
        ids = value.split(",")
        for i in ids:
            supplier_ids.append(int(i))
        queryset = queryset.filter(user_id__supplier__id__in=supplier_ids, status=1, is_active=True, is_confirmed=1, valid_to__gte=timezone.now(), valid_from__lte=timezone.now())
        return queryset

    def filter_company_name(self, queryset, name, value):
        queryset = queryset.filter(user_id__supplier__company_full_name__icontains=value)
        return queryset

    def exclude_by_id_list(self, queryset, name, value):
        if value is not None and value != "":
            queryset = queryset.exclude(id__in=[s for s in value.split(",") if s.isdigit()])
        return queryset        
        
class UserDiamondSponsorInterface(relay.Node):
    class Meta:
        name = "UserDiamondSponsorInterface"

    @classmethod
    def to_global_id(cls, type, id):
        return id

    @staticmethod
    def get_node_from_global_id(info, global_id, only_type=None):
        return UserDiamondSponsor.objects.get(id=global_id)


class UserDiamondSponsorConnection(Connection):
    reach = graphene.Boolean()

    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_reach(root, info, **kwargs):
        user = None
        if info.context.headers.get('Authorization'):
            key = info.context.headers.get('Authorization').split(" ")[-1]
            token = Token.objects.filter(key=key).first()
            if token is not None:
                user = token.user
        diamondSponsorCount = UserDiamondSponsor.objects.filter(
            status = 1,
            is_active = True,
            is_confirmed = 1,
            valid_to__gte = timezone.now(),
            valid_from__lte = timezone.now()
        ).count()
        for userDiamondSponsorNode in root.edges:
            user_diamond_sponsor = userDiamondSponsorNode.node
            if user and user.isSupplier():
                if user.supplier_sub_account.exists():
                    if user.supplier_sub_account.first().supplier.user == user_diamond_sponsor.user:
                        continue
                else:
                    if user == user_diamond_sponsor.user:
                        continue
            userDiamondSponsorNode.node.reach_number = userDiamondSponsorNode.node.reach_number + 1
            userDiamondSponsorNode.node.reach_number_count = userDiamondSponsorNode.node.reach_number_count + 1
            if userDiamondSponsorNode.node.reach_number >= diamondSponsorCount:
                userDiamondSponsorNode.node.reach_number = 0
            userDiamondSponsorNode.node.save()
        return True

class UserDiamondSponsorNode(DjangoObjectType):
    icon = graphene.String()

    class Meta:
        model = UserDiamondSponsor
        filterset_class = UserDiamondSponsorFilter
        interfaces = (CustomNode,)
        connection_class = UserDiamondSponsorConnection
        convert_choices_to_enum = False

    def resolve_image(self, info):
        if self.image and hasattr(self.image, "url"):
            if self.image.url.lower().replace('/media/', '').startswith("http"):
                return self.image
            else:
                return info.context.build_absolute_uri(self.image.url)
        else:
            return None
    
    def resolve_icon(self, info):
        if self.user.supplier.company_logo and hasattr(self.user.supplier.company_logo, "url"):
            if self.user.supplier.company_logo.url.lower().replace('/media/', '').startswith("http"):
                return self.user.supplier.company_logo
            else:
                return info.context.build_absolute_uri(self.user.supplier.company_logo.url)
        else:
            return None

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter(user_diamond_sponsor_payment__history__status=2).order_by("id")
            elif token.user.isBuyer():
                queryset = queryset.filter(
                    status=1,
                    is_active=True,
                    is_confirmed=1,
                    valid_to__gte=timezone.now(),
                    valid_from__lte=timezone.now()
                )
            return queryset
        except:
            return queryset.filter(
                status=1,
                is_active=True,
                is_confirmed=1,
                valid_to__gte=timezone.now(),
                valid_from__lte=timezone.now()
            )


class SupplierSICPFileFilter(FilterSet):
    file_type_filter = django_filters.NumberFilter(method="filter_file_type")
    latest_file_type = django_filters.NumberFilter(method="filter_user_or_admin_upload")
    user_file = django_filters.BooleanFilter(method="filter_user_file")
    class Meta:
        model = SupplierSICPFile
        fields =  ['id']

    order_by = OrderingFilter(fields=('id', 'sicp_type'))

    def filter_user_file(self, queryset, name, value):
        return queryset.filter(user_or_admin=1)

    def filter_user_or_admin_upload(self, queryset, name, value):
        key = self.request.headers['Authorization'].split(" ")
        key = key[-1]
        token = Token.objects.get(key=key)
        user = token.user
        if user.isSupplier():
            f = queryset.filter(user_or_admin=3, sicp__supplier_id=user.get_profile().id).order_by("-ordered").first()
            if f is not None:
                queryset = queryset.filter(Q(user_or_admin=3, ordered=f.ordered) | Q(sicp_type=value)).distinct().order_by("id") 
            else:
                queryset = queryset.filter(Q(user_or_admin=3) | Q(sicp_type=value)).distinct().order_by("id") 
        return queryset

    def filter_file_type(self, queryset, name, value):
        f = queryset.filter(sicp_type=value).order_by("-ordered").first()
        l = queryset.filter(user_or_admin=3, sicp_id=f.sicp_id).order_by("-ordered").first()     
        if f is not None:
            if l is not None:
                queryset = queryset.filter(Q(user_or_admin=3, ordered=l.ordered) | Q(sicp_type=value, ordered=f.ordered)).distinct().order_by("id")
            else:
                queryset = queryset.filter(Q(user_or_admin=3) | Q(sicp_type=value, ordered=f.ordered)).distinct().order_by("id")
        else:
            queryset = queryset.none()
        return queryset

class SupplierSICPFileNode(DjangoObjectType):
    class Meta:
        model = SupplierSICPFile
        filterset_class = SupplierSICPFileFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

    def resolve_file_name(self, info):
        if "sicp_file" in str(self.file_name):
            return info.context.build_absolute_uri(self.file_name.url)
        return ""

class SupplierSICPFilter(FilterSet):
    supplier_id = django_filters.CharFilter(field_name="supplier_id", lookup_expr="exact")  
    latest_files = django_filters.NumberFilter(method="lates_file_filter")
    account_id = django_filters.CharFilter(method="account_id_filter")
    account_name = django_filters.CharFilter(method="account_name_filter")
    account_email = django_filters.CharFilter(method="account_email_filter")
    sicp_registration = django_filters.CharFilter(method="sicp_registration_filter")
    date_created_from = django_filters.DateTimeFilter(field_name="created_date", lookup_expr="gte")
    date_created_to = django_filters.DateTimeFilter(field_name="created_date", lookup_expr="lte")
    date_created = django_filters.DateTimeFilter(field_name="created_date", lookup_expr="exact")
    file_filter = django_filters.NumberFilter(method="filter_file_type")
    sicp_type_filter = django_filters.BooleanFilter(method="sort", lookup_expr="exact")
    sanction_check_filter = django_filters.BooleanFilter(method="filter_sanction_check", lookup_expr="exact")
    class Meta:
        model = SupplierSICP
        fields = {
            'id': ['exact'],
            'is_reviewed': ['exact'],
            'is_confirmed': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            'id', 
            'is_reviewed', 
            'is_confirmed',
            'created_date',
            ('sicp_files__sicp_type', 'sicp_type'),
            ('supplier__user__username', 'account_id'),
            ('supplier__company_full_name', 'company_name'),
            ('supplier__user__email', 'company_email'),
            ('supplier__sicp_registration__sicp_type', 'sicp_registration'),
        )
    )

    def sort(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isSupplier():
                if value:
                    queryset = queryset.filter(sicp_files__user_or_admin=1, supplier_id=user.get_profile().id).distinct().order_by("sicp_files__sicp_type") 
                else:
                    queryset = queryset.filter(sicp_files__user_or_admin=1, supplier_id=user.get_profile().id).distinct().order_by("-sicp_files__sicp_type")
                return queryset
        except:
            raise Exception("You must log in")

    def filter_sanction_check(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                if value:
                    queryset = queryset.exclude(sanction_check__isnull=True).exclude(sanction_check__exact='')
                return queryset.order_by("supplier").distinct("supplier")
        except:
            raise Exception("You must log in") 


    def filter_file_type(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                supplier_ids = map(
                    lambda x: x.get('supplier_id'),
                    SupplierSICP.objects.all().values('supplier_id').distinct(),
                )

                order = []
                count = 0
                status = True
                for i in supplier_ids:
                    f = SupplierSICPFile.objects.filter(sicp_type=value, sicp__supplier_id=i).order_by("-ordered").first()
                    if f is not None:
                        status = False
                        if count == 0:
                            temp = queryset.filter(sicp_files__sicp_type=value, sicp_files__ordered=f.ordered, supplier_id=i)
                            count = count + 1              
                        else:
                            temp = temp | queryset.filter(sicp_files__sicp_type=value, sicp_files__ordered=f.ordered, supplier_id=i)                  
                            count = count + 1
                if status:
                    temp = queryset.none()
                return temp.distinct().order_by("id")
        except:
            raise Exception("You must log in")

    def lates_file_filter(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isSupplier():
                f = SupplierSICPFile.objects.filter(sicp_type=value, sicp__supplier_id=user.get_profile().id).order_by("-ordered").first()
                if f is not None:
                    queryset = queryset.filter(sicp_files__sicp_type=value, sicp_files__ordered=f.ordered, supplier_id=user.get_profile().id).distinct().order_by("id") 
                else:
                    queryset = queryset.none()
                return queryset
        except:
            raise Exception("You must log in")

    def account_id_filter(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                queryset = queryset.filter(supplier__user__username__icontains=value)     
                return queryset.order_by("id")
            else:
                raise Exception(UserError.USER_12)                      
        except:
            raise Exception("You must log in")

    def account_name_filter(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                queryset = queryset.filter(supplier__company_full_name__icontains=value)     
                return queryset.order_by("id")
            else:
                raise Exception(UserError.USER_12)                      
        except:
            raise Exception("You must log in")

    def account_email_filter(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                queryset = queryset.filter(supplier__user__email__icontains=value)     
                return queryset.order_by("id")
            else:
                raise Exception(UserError.USER_12)                      
        except:
            raise Exception("You must log in")

    def sicp_registration_filter(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                queryset = queryset.filter(supplier__sicp_registration__sicp_type__exact=value)     
                return queryset.order_by("id")
            else:
                raise Exception(UserError.USER_12)                      
        except:
            raise Exception("You must log in")

class SupplierSICPNode(DjangoObjectType):
    class Meta:
        model = SupplierSICP
        filterset_class = SupplierSICPFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():                
                queryset = queryset.all().order_by("id")
            elif token.user.isSupplier():
                queryset = queryset.filter(supplier__user_id=token.user_id)                    
            return queryset
        except:
            raise Exception("You must log in")

class SupplierSICPRegistrationUpdate(graphene.Mutation):
    status = graphene.Boolean()
    supplier = graphene.Field(SupplierNode)
    error = graphene.Field(Error)

    class Arguments:
        supplier_id = graphene.String(required=True)
        sicp_registration_id = graphene.String(required=True)

    def mutate(root, info, supplier_id, sicp_registration_id):
        supplier_instance = Supplier.objects.filter(id=supplier_id).first()
        sicp_registration_instance = SICPRegistration.objects.filter(id=sicp_registration_id).first()
        if supplier_instance is not None and sicp_registration_instance is not None:
            supplier_instance.sicp_registration = sicp_registration_instance
            supplier_instance.save()
            return SupplierSICPRegistrationUpdate(status=True, supplier=supplier_instance)
        else:
            return SupplierSICPRegistrationUpdate(status=False, supplier=None)

class SICPTextEditorFilter(FilterSet):
    sicp_type_filter = django_filters.CharFilter(method="filter_sicp_type")
    class Meta:
        model = SICPTextEditor
        fields =  ['id']

    order_by = OrderingFilter(fields=('id', 'sicp_type'))

    def filter_sicp_type(self, queryset, name, value):
        return queryset.filter(sicp_type=value)

class SICPTextEditorNode(DjangoObjectType):
    class Meta:
        model = SICPTextEditor
        filterset_class = SICPTextEditorFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

class SICPTextEditorFileFilter(FilterSet):
    class Meta:
        model = SICPTextEditorFile
        fields =  ['id']

    order_by = OrderingFilter(fields=('id', 'sicp_text_editor'))

class SICPTextEditorFileNode(DjangoObjectType):
    class Meta:
        model = SICPTextEditorFile
        filterset_class = SICPTextEditorFileFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

    def resolve_file_name(self, info):
        if "sicp_text_editor_file" in str(self.file_name):
            return info.context.build_absolute_uri(self.file_name.url)
        return ""

class UserDiamondSponsorFeeFilter(FilterSet):
    class Meta:
        model = UserDiamondSponsorFee
        fields =  ['id', 'title', 'fee']

    order_by = OrderingFilter(fields=('id', 'title', 'fee'))

class UserDiamondSponsorFeeNode(DjangoObjectType):
    class Meta:
        model = UserDiamondSponsorFee
        filterset_class = UserDiamondSponsorFeeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

class UserRatingSupplierProductFilter(FilterSet):
    class Meta:
        model = UserRatingSupplierProduct
        fields = ['id', 'user_id', 'supplier_product_id']
    
    order_by = OrderingFilter(fields=('user_id', 'supplier_product_id'))

class UserRatingSupplierProductNode(DjangoObjectType):
    class Meta:
        model = UserRatingSupplierProduct
        filterset_class = UserRatingSupplierProductFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

class Mutation(graphene.ObjectType):
    supplier_flash_sale_create = SupplierFlashSaleCreate.Field()
    supplier_flash_sale_update = SupplierFlashSaleUpdate.Field()
    supplier_flash_sale_delete = SupplierFlashSaleDelete.Field()
    supplier_flash_sale_reorder_update = SupplierFlashSaleUpdateOrder.Field()
    supplier_sicp_registration_update = SupplierSICPRegistrationUpdate.Field()

    buyer_create = BuyerCreate.Field()
    buyer_update = BuyerUpdate.Field()
    buyer_profile_update = BuyerProfileUpdate.Field()
    buyer_status_update = BuyerStatusUpdate.Field()

    buyer_sub_accounts_create = BuyerSubAccountsCreate.Field()
    buyer_sub_accounts_status_update = BuyerSubAccountsStatusUpdate.Field()

    supplier_create = SupplierCreate.Field()
    supplier_update = SupplierUpdate.Field()
    supplier_profile_update = SupplierProfileUpdate.Field()
    supplier_status_update = SupplierStatusUpdate.Field()
    supplier_email_update = SupplierEmailUpdate.Field()

    admin_create = AdminCreate.Field()
    admin_update = AdminUpdate.Field()
    admin_delete = AdminDelete.Field()
    admin_status_update = AdminStatusUpdate.Field()
    admin_profile_update = AdminProfileUpdate.Field()

    group_create = GroupCreate.Field()
    group_permission_create = GroupPermissionCreate.Field()
    group_delete = GroupDelete.Field()

    user_permission_status_update = UsersPermissionUpdateStatus.Field()

    user_substitution_permission_create = UserSubstitutionPermissionCreate.Field()
    user_substitution_permission_update = UserSubstitutionPermissionUpdate.Field()
    user_substitution_permission_status_update = UserSubstitutionPermissionUpdateStatus.Field()

    supplier_profile_company_update = SupplierProfileCompanyUpdate.Field()
    buyer_profile_company_update = BuyerProfileCompanyUpdate.Field()

    supplier_flash_sale_status_update = SupplierFlashSaleUpdateStatus.Field()
    supplier_flash_sale_is_confirmed_update = SupplierFlashSaleIsConfirmedUpdate.Field()
    supplier_flash_sale_create_text_editer = SupplierFlashSaleTextEditer.Field()


class Query(ObjectType):
    supplier = CustomNode.Field(SupplierNode)
    suppliers = CustomizeFilterConnectionField(SupplierNode)

    supplier_flash_sale = CustomNode.Field(SupplierFlashSaleNode)
    supplier_flash_sales = CustomizeFilterConnectionField(SupplierFlashSaleNode)
    
    def resolve_supplier_flash_sales(self, info, **kwargs):
        return SupplierFlashSale.objects.all()

    supplier_product = CustomNode.Field(SupplierProductNode)
    supplier_product_list = CustomizeFilterConnectionField(SupplierProductNode, flag=graphene.Boolean(), orderRandom=graphene.Boolean())
    supplier_product_same_category_list = CustomizeFilterConnectionField(SupplierProductNode, supplier_product_id = graphene.String(required=True), flag=graphene.Boolean())
    
    def resolve_supplier_product_list(self, info, **kwargs):        
        queryset = SupplierProduct.objects.all().order_by("id")

        isOrderRandom = kwargs.get("orderRandom")
        numItems = kwargs.get("first")
        if isOrderRandom is not None and isOrderRandom == True and numItems is not None and numItems>1:
            pks = list(SupplierProduct.objects.values_list('pk', flat=True))
            num = kwargs.get("first")
            random_pks_list = random.sample(pks,num)
            queryset = queryset.filter(pk__in=random_pks_list)

        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if kwargs.get("flag"):
                value = kwargs.get("flag")
                if user.isSupplier():
                    if value:
                        queryset = queryset.filter(user_supplier__user_id=user.id).distinct()
                    else:
                        queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)
                elif not user.isAdmin():
                    queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)
                else:
                    queryset = queryset.exclude(confirmed_status=ProductConfirmStatus.DRAFT)
            else:
                if user.isAdmin():
                    queryset = queryset.exclude(confirmed_status=ProductConfirmStatus.DRAFT)
                else:
                    queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)

        except Exception as error:
            queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)

        return queryset

    def resolve_supplier_product_same_category_list(self, info, supplier_product_id, **kwargs):
        supplier_product = SupplierProduct.objects.filter(id = supplier_product_id).first()
        if supplier_product is None:
            return None
        cluster_code_list = list(set([x.category.sub_cluster_code.cluster_code for x in supplier_product.supplier_product_category_list.all()]))
        sub_cluster_code_list = list(set([x.category.sub_cluster_code for x in supplier_product.supplier_product_category_list.all()]))
        category_list = list(set([x.category for x in supplier_product.supplier_product_category_list.all()]))
        queryset = SupplierProduct.objects.filter(
            supplier_product_category_list__category__sub_cluster_code__cluster_code__in = cluster_code_list
        ).exclude(id=supplier_product_id).exclude(user_supplier=supplier_product.user_supplier).annotate(
            same_category = Count(
                "supplier_product_category_list",
                filter = Q(supplier_product_category_list__category__in = category_list),
                distinct = True
            ),
            same_sub_cluster_code = Count(
                "supplier_product_category_list",
                filter = Q(supplier_product_category_list__category__sub_cluster_code__in = sub_cluster_code_list),
                distinct = True
            ),
            same_cluster_code = Count(
                "supplier_product_category_list",
                filter = Q(supplier_product_category_list__category__sub_cluster_code__cluster_code__in = cluster_code_list),
                distinct = True
            ),
        ).order_by(
            "-same_category",
            "-same_sub_cluster_code", 
            "-same_cluster_code",
            "-user_supplier__profile_features__profile_features_type"
        ).distinct()
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if kwargs.get("flag"):
                value = kwargs.get("flag")
                if user.isSupplier():
                    if value:
                        queryset = queryset.filter(user_supplier__user_id=user.id)
                    else:
                        queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)
                elif not user.isAdmin():
                    queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)
                else:
                    queryset = queryset.exclude(confirmed_status=ProductConfirmStatus.DRAFT)
            else:
                if user.isAdmin():
                    queryset = queryset.exclude(confirmed_status=ProductConfirmStatus.DRAFT)
                else:
                    queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)
        except:
            queryset = queryset.filter(is_visibility=True, confirmed_status=ProductConfirmStatus.APPROVED)
            
        return queryset

    user = CustomNode.Field(UserNode)
    users = CustomizeFilterConnectionField(UserNode)

    buyer = CustomNode.Field(BuyerNode)
    buyers = CustomizeFilterConnectionField(BuyerNode)
    buyer_activity = CustomNode.Field(BuyerActivityNode)
    buyer_activities = CustomizeFilterConnectionField(BuyerActivityNode)
    buyer_industry = CustomNode.Field(BuyerIndustryNode)
    buyer_industries = CustomizeFilterConnectionField(BuyerIndustryNode)

    buyer_sub_account = CustomNode.Field(BuyerSubAccountsNode)
    buyer_sub_accounts = CustomizeFilterConnectionField(BuyerSubAccountsNode)
    buyer_sub_account_activity = CustomNode.Field(BuyerSubAccountsActivityNode)
    buyer_sub_account_activities = CustomizeFilterConnectionField(BuyerSubAccountsActivityNode)

    supplier_portfolio = CustomNode.Field(PortfolioNode)
    supplier_portfolios = CustomizeFilterConnectionField(PortfolioNode)

    supplier_industry = CustomNode.Field(SupplierIndustryNode)
    supplier_industries = CustomizeFilterConnectionField(SupplierIndustryNode)

    supplier_category = CustomNode.Field(SupplierCategoryNode)
    supplier_categories = CustomizeFilterConnectionField(SupplierCategoryNode)

    supplier_client_focus = CustomNode.Field(SupplierClientFocusNode, )
    supplier_client_focuses = CustomizeFilterConnectionField(SupplierClientFocusNode)

    supplier_activity = CustomNode.Field(SupplierActivityNode)
    supplier_activities = CustomizeFilterConnectionField(SupplierActivityNode)

    admin = CustomNode.Field(AdminNode)
    admins = CustomizeFilterConnectionField(AdminNode)

    group = CustomNode.Field(GroupNode)
    groups = CustomizeFilterConnectionField(GroupNode)

    group_permission = CustomNode.Field(GroupPermissionNode)
    group_permissions = CustomizeFilterConnectionField(GroupPermissionNode)

    user_permission = CustomNode.Field(UsersPermissionNode)
    user_permissions = CustomizeFilterConnectionField(UsersPermissionNode)

    user_profile = graphene.Field(UserNode)

    def resolve_user_profile(self, info):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            user = User.objects.select_related('admin').get(id=token.user.id)
        if token.user.isBuyer():
            user = User.objects.select_related('buyer').get(id=token.user.id)
        if token.user.isSupplier():
            user = User.objects.select_related('supplier').get(id=token.user.id)
        return user

    user_substitution_permission = CustomNode.Field(UserSubstitutionPermissionNode)
    user_substitution_permissions = CustomizeFilterConnectionField(UserSubstitutionPermissionNode)

    profile = graphene.Field(UserInterface, required=True)

    def resolve_profile(root, info):
        token = GetToken.getToken(info)
        if token.user.isAdmin():
            if not hasattr(token.user, "admin"):
                Admin.objects.create(user=token.user)
            return Admin.objects.get(id=token.user.admin.id)

        if token.user.isBuyer() and token.user.company_position == 1:
            return Buyer.objects.get(id=token.user.buyer.id)

        if token.user.isSupplier() and token.user.company_position == 1:
            return Supplier.objects.get(id=token.user.supplier.id)

        if token.user.isBuyer() and token.user.company_position == 2:
            buyer_sub_account = BuyerSubAccounts.objects.get(user=token.user)
            return buyer_sub_account

        if token.user.isSupplier() and token.user.company_position == 2:
            return SupplierSubAccount.objects.get(user=token.user)

    supplier_sub_account = CustomNode.Field(SupplierSubAccountNode)
    supplier_sub_accounts = CustomizeFilterConnectionField(SupplierSubAccountNode)
    supplier_sub_account_activity = CustomNode.Field(SupplierSubAccountActivityNode)
    supplier_sub_account_activities = CustomizeFilterConnectionField(SupplierSubAccountActivityNode)

    user_diamond_sponsor = CustomNode.Field(UserDiamondSponsorNode)
    user_diamond_sponsors = CustomizeFilterConnectionField(
        UserDiamondSponsorNode,
        family_code = graphene.String(),
        cluster_code = graphene.String(),
        sub_cluster_code = graphene.String(),
        category = graphene.String(),
        flag = graphene.Boolean()
    )

    def resolve_user_diamond_sponsors(root, info, **kwargs):
        queryset = UserDiamondSponsor.objects.all()
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isSupplier():
                if kwargs.get("flag"):
                    queryset = queryset.filter(user_id=user.id)
                else:
                    queryset = queryset.filter(status=1, is_active=True, is_confirmed=1, valid_to__gte=timezone.now(), valid_from__lte=timezone.now())
            elif not user.isAdmin():
                queryset = queryset.filter(status=1, is_active=True, is_confirmed=1, valid_to__gte=timezone.now(), valid_from__lte=timezone.now())
            queryset = queryset
        except Exception as error:
            queryset = queryset.filter(status=1, is_active=True, is_confirmed=1, valid_to__gte=timezone.now(), valid_from__lte=timezone.now())

        if kwargs.get("category") is not None and kwargs.get("category") != "":
            category = Category.objects.filter(id=kwargs.get("category")).first()
            if category is not None:
                queryset = queryset.filter(
                    user__supplier__suppliercategory__category__sub_cluster_code__cluster_code=category.sub_cluster_code.cluster_code
                ).annotate(
                    has_category = ExpressionWrapper(
                        Q(user__supplier__suppliercategory__category=category),
                        output_field=BooleanField()
                    ),
                    has_sub_cluster_code = ExpressionWrapper(
                        Q(user__supplier__suppliercategory__category__sub_cluster_code=category.sub_cluster_code),
                        output_field=BooleanField()
                    )
                ).order_by("-has_category", "-has_sub_cluster_code", "-reach_number", "-user__supplier__profile_features__profile_features_type", "valid_from")
            else:
                queryset = queryset.none()
        elif kwargs.get("sub_cluster_code") is not None and kwargs.get("sub_cluster_code") != "":
            sub_cluster_code = SubClusterCode.objects.filter(id=kwargs.get("sub_cluster_code")).first()
            if sub_cluster_code is not None:
                queryset = queryset.filter(
                    user__supplier__suppliercategory__category__sub_cluster_code__cluster_code=sub_cluster_code.cluster_code
                ).annotate(
                    has_sub_cluster_code = ExpressionWrapper(
                        Q(user__supplier__suppliercategory__category__sub_cluster_code=sub_cluster_code),
                        output_field=BooleanField()
                    )
                ).order_by("-has_sub_cluster_code", "-reach_number", "-user__supplier__profile_features__profile_features_type", "valid_from")            
            else:
                queryset = queryset.none()
        elif kwargs.get("cluster_code") is not None and kwargs.get("cluster_code") != "":
            cluster_code = ClusterCode.objects.filter(id=kwargs.get("cluster_code")).first()
            if cluster_code is not None:
                queryset = queryset.filter(
                    user__supplier__suppliercategory__category__sub_cluster_code__cluster_code_id=kwargs.get("cluster_code")
                ).order_by("-reach_number", "-user__supplier__profile_features__profile_features_type", "valid_from")
            else:
                queryset = queryset.none()
        elif kwargs.get("family_code") is not None and kwargs.get("family_code") != "":
            family_code = FamilyCode.objects.filter(id=kwargs.get("family_code")).first()
            if family_code is not None:
                queryset = queryset.filter(
                    user__supplier__suppliercategory__category__sub_cluster_code__cluster_code__family_code_id=kwargs.get("family_code")
                ).order_by("-reach_number", "-user__supplier__profile_features__profile_features_type", "valid_from")
            else:
                queryset = queryset.none()
        else:
            queryset = queryset.order_by("-reach_number", "-user__supplier__profile_features__profile_features_type", "valid_from")
        return queryset.distinct()

    user_supplier_sicp = CustomNode.Field(SupplierSICPNode)
    user_supplier_sicps = CustomizeFilterConnectionField(SupplierSICPNode)
    user_supplier_sicp_text_editor = CustomizeFilterConnectionField(SICPTextEditorNode)

    user_diamond_sponsor_fee = CustomNode.Field(UserDiamondSponsorFeeNode)
    user_diamond_sponsor_fees = CustomizeFilterConnectionField(UserDiamondSponsorFeeNode)

    user_following_supplier = CustomNode.Field(UserFollowingSupplierNode)
    user_following_suppliers = CustomizeFilterConnectionField(UserFollowingSupplierNode)

    user_rating_supplier_product = CustomNode.Field(UserRatingSupplierProductNode)
    user_rating_supplier_products = CustomizeFilterConnectionField(UserRatingSupplierProductNode)
