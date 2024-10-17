import graphene
import django_filters
import graphene_django_optimizer as gql_optimizer
from apps.core import CustomNode, CustomizeFilterConnectionField, Error
from apps.master_data.error_code import MasterDataError
from apps.master_data.models import (
    Industry,
    ClientFocus,
    FamilyCode,
    ClusterCode,
    SubClusterCode,
    Category,
    Sponsor,
    Currency,
    Level,
    Country,
    CountryState,
    NumberofEmployee,
    IndustrySectors,
    IndustryCluster,
    IndustrySubSectors,
    Reason,
    Language,
    Promotion,
    ContractType,
    PaymentTerm,
    DeliveryTerm,
    UnitofMeasure,
    EmailTemplates,
    Gender,
    TechnicalWeighting,
    AuctionType,
    Position,
    SupplierList,
    EmailList,
    ExchangeRate,
    Coupon,
    Bank,
    CountryTranslation,
    CountryStateTranslation,
    CurrencyTranslation,
    ContractTypeTranslation,
    PaymentTermTranslation,
    DeliveryTermTranslation,
    UnitofMeasureTranslation,
    EmailTemplatesTranslation,
    GenderTranslation,
    TechnicalWeightingTranslation,
    AuctionTypeTranslation,
    PositionTranslation,
    LevelTranslation,
    NumberofEmployeeTranslation,
    IndustryTranslation,
    IndustryClusterTranslation,
    IndustrySectorsTranslation,
    IndustrySubSectorsTranslation,
    ClientFocusTranslation,
    FamilyCodeTranslation,
    ClusterCodeTranslation,
    SubClusterCodeTranslation,
    CategoryTranslation,
    SponsorTranslation,
    ReasonTranslation,
    LanguageTranslation,
    PromotionTranslation,
    SupplierListTranslation,
    PromotionUserUsed,
    PromotionApplyScope,
    Voucher,
    VoucherTranslation,
    BuyerClubVoucher,
    BuyerClubVoucherTranslation,
    WarrantyTerm,
    WarrantyTermTranslation,
    SetProductAdvertisement,
    SetProductAdvertisementTranslation,
)
from apps.users.models import Token, User
from datetime import datetime
from django_filters import FilterSet, OrderingFilter
from django.core.mail import send_mail
from django.db.models import Count, Q, Subquery
from django.db.models.functions import Lower
from django.template import Template, Context
from django.utils import timezone, translation
from django.db import transaction

from graphene import relay, Connection
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError

def send_mail_promotion(promotion_user_used, user, profile_name, profile_amount, commission_amount):
    promotion = promotion_user_used.promotion
    user_name = None
    if promotion_user_used.user_used_email is not None and promotion.user_given_email is not None:
        language_code = user.language.item_code
        email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code='PromotionRecommandation', language_code=language_code)

        if not email_template:
            email_template = EmailTemplates.objects.filter(item_code='PromotionRecommandation')

        email_template = email_template.first()

        if user.isSupplier():
            user_name = user.supplier.company_full_name
        elif user.isBuyer():
            user_name = user.buyer.company_full_name

        messages = Template(email_template.content).render(
            Context(
                {
                    "pro_code": promotion.name,
                    "image": "https://api.nextpro.io/static/logo_mail.png",
                    "name": promotion.user_given,
                    "user_name": user_name,
                    "profile_name": profile_name,
                    "profile_amount": profile_amount,
                    "commission": promotion.commission,
                    "commission_amount": commission_amount,
                }
            )
        )
        title = Template(email_template.title).render(Context({"pro_code": promotion.name, }))
        try:
            send_mail(
                title,
                messages,
                'NextPro <no-reply@nextpro.io>',
                [promotion.user_given_email],
                html_message=messages,
                fail_silently=False,
            )
        except Exception as error:
            print(error)
            print("+++++++")


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length


class GetToken:
    def getToken(info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            return token
        except:
            raise GraphQLError("Invalid token")


class CurrencyFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Currency
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class CurrencyTranslationNode(DjangoObjectType):
    class Meta:
        model = CurrencyTranslation
        filter_fields = ['id']


class CurrencyNode(DjangoObjectType):
    class Meta:
        model = Currency
        filterset_class = CurrencyFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('item_code'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('item_code'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('item_code'))
        return queryset


class ContractTypeFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = ContractType
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = ContractType.objects.filter(name__icontains=value).exclude(translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class ContractTypeTranslationNode(DjangoObjectType):
    class Meta:
        model = ContractTypeTranslation
        filter_fields = ['id']


class ContractTypeNode(DjangoObjectType):
    class Meta:
        model = ContractType
        filterset_class = ContractTypeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class PaymentTermFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = PaymentTerm
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class PaymentTermTranslationNode(DjangoObjectType):
    class Meta:
        model = PaymentTermTranslation
        filter_fields = ['id']


class PaymentTermNode(DjangoObjectType):
    class Meta:
        model = PaymentTerm
        filterset_class = PaymentTermFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    def resolve_translations(self, info):
        if hasattr(self, 'translations'):
            return self.translations
        return self.translations.all()

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class DeliveryTermFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = DeliveryTerm
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class DeliveryTermTranslationNode(DjangoObjectType):
    class Meta:
        model = DeliveryTermTranslation
        filter_fields = ['id']


class DeliveryTermNode(DjangoObjectType):
    class Meta:
        model = DeliveryTerm
        filterset_class = DeliveryTermFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class UnitofMeasureFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = UnitofMeasure
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class UnitofMeasureTranslationNode(DjangoObjectType):
    class Meta:
        model = UnitofMeasureTranslation
        filter_fields = ['id']


class UnitofMeasureNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = UnitofMeasure
        filterset_class = UnitofMeasureFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    def resolve_translations(self, info):
        if hasattr(self, 'translations'):
            return self.translations
        return self.translations.all()

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('item_code'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('item_code'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('item_code'))
        return queryset


class EmailTemplatesFilter(FilterSet):
    title = django_filters.CharFilter(method="fillter_by_title")
    title_vi = django_filters.CharFilter(method="fillter_by_title_vi")
    title_en = django_filters.CharFilter(method="fillter_by_title_en")

    class Meta:
        model = EmailTemplates
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__title', 'title'),
        )
    )

    def fillter_by_title(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__title__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_title_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__title__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_title_en(self, queryset, name, value):
        queryset = queryset.filter(translations__title__icontains=value, translations__language_code="en")
        return queryset


class EmailTemplatesTranslationNode(DjangoObjectType):
    class Meta:
        model = EmailTemplatesTranslation
        filter_fields = ['id']


class EmailTemplatesNode(DjangoObjectType):
    class Meta:
        model = EmailTemplates
        filterset_class = EmailTemplatesFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_title(self, info):
        return self.translated.title

    def resolve_content(self, info):
        return self.translated.content

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('title'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('title'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('title'))
        return queryset


class GenderFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Gender
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class GenderTranslationNode(DjangoObjectType):
    class Meta:
        model = GenderTranslation
        filter_fields = ['id']


class GenderNode(DjangoObjectType):
    class Meta:
        model = Gender
        filterset_class = GenderFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class TechnicalWeightingFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = TechnicalWeighting
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class TechnicalWeightingTranslationNode(DjangoObjectType):
    class Meta:
        model = TechnicalWeightingTranslation
        filter_fields = ['id']


class TechnicalWeightingNode(DjangoObjectType):
    class Meta:
        model = TechnicalWeighting
        filterset_class = TechnicalWeightingFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class AuctionTypeFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = AuctionType
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class AuctionTypeTranslationNode(DjangoObjectType):
    class Meta:
        model = AuctionTypeTranslation
        filter_fields = ['id']


class AuctionTypeNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = AuctionType
        filterset_class = AuctionTypeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class PositionFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Position
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class PositionTranslationNode(DjangoObjectType):
    class Meta:
        model = PositionTranslation
        filter_fields = ['id']


class PositionNode(DjangoObjectType):
    class Meta:
        model = Position
        filterset_class = PositionFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class LevelFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Level
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class LevelTranslationNode(DjangoObjectType):
    class Meta:
        model = LevelTranslation
        filter_fields = ['id']


class LevelNode(DjangoObjectType):
    class Meta:
        model = Level
        filterset_class = LevelFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class NumberofEmployeeFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = NumberofEmployee
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(fields=('name', 'status'))

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class NumberofEmployeeTranslationNode(DjangoObjectType):
    class Meta:
        model = NumberofEmployeeTranslation
        filter_fields = ['id']


class NumberofEmployeeNode(DjangoObjectType):
    class Meta:
        model = NumberofEmployee
        filterset_class = NumberofEmployeeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class CountryFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Country
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(fields=('item_code', 'name', 'status'))

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class CountryTranslationNode(DjangoObjectType):
    class Meta:
        model = CountryTranslation
        filter_fields = ['id']


class CountryNode(DjangoObjectType):
    class Meta:
        model = Country
        filterset_class = CountryFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
            else:
                queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)

        except Exception as err:
            print('exception err {}'.format(err))
            queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        return queryset


class CountryStateFilter(FilterSet):
    name = django_filters.CharFilter(method="filter_by_name")
    country_id = django_filters.CharFilter(method="filter_by_country_id")
    state_code_contains = django_filters.CharFilter(method="filter_by_state_code_contains")
    country_name_contains = django_filters.CharFilter(method="filter_by_country_name_contains")

    class Meta:
        model = CountryState
        fields = {
            'id': ['exact'],
            'state_code': ['exact'],
            'status': ['exact'],
            'country_id': ['exact'],
        }

    order_by = OrderingFilter(fields=('state_code', 'name', 'status'))

    def filter_by_name(self, queryset, name, value):
        query = Q()
        query.add(Q(name__icontains=value), Q.OR)
        query.add(Q(translations__name__icontains=value), Q.OR)
        queryset_translation = queryset.filter(query)
        return queryset_translation

    def filter_by_country_id(self, queryset, name, value):
        queryset = queryset.filter(country__id__exact=value)
        return queryset

    def filter_by_state_code_contains(self, queryset, name, value):
        queryset = queryset.filter(state_code__icontains=value)
        return queryset

    def filter_by_country_name_contains(self, queryset, name, value):
        queryset = queryset.filter(country__name__icontains=value)
        return queryset


class CountryStateTranslationNode(DjangoObjectType):
    class Meta:
        model = CountryStateTranslation
        filter_fields = ['id']


class CountryStateNode(DjangoObjectType):
    class Meta:
        model = CountryState
        filterset_class = CountryStateFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        query = Q()
        query.add(~Q(state_code="UNKNOWN"), Q.AND)
        try:
            user = GetToken.getToken(info).user
            if not user.isAdmin():
                query.add(Q(status=True), Q.AND)
            queryset = gql_optimizer.query(queryset.filter(query).order_by('id'), info)
        except:
            query.add(Q(status=True), Q.AND)
            queryset = gql_optimizer.query(queryset.filter(query).order_by('id'), info)
        return queryset


class IndustryFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Industry
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class IndustryTranslationNode(DjangoObjectType):
    class Meta:
        model = IndustryTranslation
        filter_fields = ['id']


class IndustryNode(DjangoObjectType):
    class Meta:
        model = Industry
        filterset_class = IndustryFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('item_code')
            else:
                queryset = queryset.filter(status=True).order_by('item_code')
        except:
            queryset = queryset.filter(status=True).order_by('item_code')
        return queryset


class IndustryClusterFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = IndustryCluster
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class IndustryClusterTranslationNode(DjangoObjectType):
    class Meta:
        model = IndustryClusterTranslation
        filter_fields = ['id']


class IndustryClusterNode(DjangoObjectType):
    class Meta:
        model = IndustryCluster
        filterset_class = IndustryClusterFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('item_code')
            else:
                queryset = queryset.filter(status=True).order_by('item_code')
        except:
            queryset = queryset.filter(status=True).order_by('item_code')
        return queryset


class IndustrySectorsFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = IndustrySectors
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class IndustrySectorsTranslationNode(DjangoObjectType):
    class Meta:
        model = IndustrySectorsTranslation
        filter_fields = ['id']


class IndustrySectorsNode(DjangoObjectType):
    class Meta:
        model = IndustrySectors
        filterset_class = IndustrySectorsFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('item_code')
            else:
                queryset = queryset.filter(status=True).order_by('item_code')
        except:
            queryset = queryset.filter(status=True).order_by('item_code')
        return queryset


class IndustrySubSectorsFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = IndustrySubSectors
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class IndustrySubSectorsTranslationNode(DjangoObjectType):
    class Meta:
        model = IndustrySubSectorsTranslation
        filter_fields = ['id']


class IndustrySubSectorsNode(DjangoObjectType):
    class Meta:
        model = IndustrySubSectors
        filterset_class = IndustrySubSectorsFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('item_code')
            else:
                queryset = queryset.filter(status=True).order_by('item_code')
        except:
            queryset = queryset.filter(status=True).order_by('item_code')
        return queryset


class SearchIndustry(graphene.Union):
    class Meta:
        types = (IndustryNode, IndustryClusterNode, IndustrySectorsNode, IndustrySubSectorsNode)


class IndustryConnection(graphene.Connection):
    class Meta:
        node = SearchIndustry

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return len(root.iterable)


class ClientFocusFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = ClientFocus
        fields = {
            'id': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class ClientFocusTranslationNode(DjangoObjectType):
    class Meta:
        model = ClientFocusTranslation
        filter_fields = ['id']


class ClientFocusNode(DjangoObjectType):
    class Meta:
        model = ClientFocus
        filterset_class = ClientFocusFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('id')
            else:
                queryset = queryset.filter(status=True).order_by('id')
        except:
            queryset = queryset.filter(status=True).order_by('id')
        return queryset


class FamilyCodeFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")
    name_level_filter = django_filters.CharFilter(method='filter_name_level')

    class Meta:
        model = FamilyCode
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def filter_name_level(self, queryset, name, value):
        queryset = queryset.filter(Q(name__icontains=value) | Q(clusterCode__name__icontains=value)).distinct().order_by("id")
        return queryset

    def fillter_by_name(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value) |
            Q(name__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value, translations__language_code="en") |
            Q(name__icontains=value)
        )
        return queryset


class FamilyCodeTranslationNode(DjangoObjectType):
    class Meta:
        model = FamilyCodeTranslation
        filter_fields = ['id']


class FamilyCodeNode(DjangoObjectType):
    class Meta:
        model = FamilyCode
        filterset_class = FamilyCodeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('id')
            else:
                queryset = queryset.filter(status=True).order_by('id')
        except:
            queryset = queryset.filter(status=True).order_by('id')
        return queryset


class ClusterCodeFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = ClusterCode
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value) |
            Q(name__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value, translations__language_code="en")
            | Q(name__icontains=value)
        )
        return queryset


class ClusterCodeTranslationNode(DjangoObjectType):
    class Meta:
        model = ClusterCodeTranslation
        filter_fields = ['id']


class ClusterCodeNode(DjangoObjectType):
    supplier_number = graphene.Int()

    class Meta:
        model = ClusterCode
        filterset_class = ClusterCodeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    def resolve_supplier_number(self, info):
        return self.subClusterCode.all().annotate(
            supplier_number=Count('category__suppliercategory__user_supplier')
        ).exclude(
            supplier_number=0
        ).values('category__suppliercategory__user_supplier', "supplier_number").count()

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('id')
            else:
                queryset = queryset.filter(status=True).order_by('id')
        except:
            queryset = queryset.filter(status=True).order_by('id')
        return queryset


class SubClusterCodeFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = SubClusterCode
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value) |
            Q(name__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value, translations__language_code="en")
            | Q(name__icontains=value)
        )
        return queryset


class SubClusterCodeTranslationNode(DjangoObjectType):
    class Meta:
        model = SubClusterCodeTranslation
        filter_fields = ['id']


class SubClusterCodeNode(DjangoObjectType):
    class Meta:
        model = SubClusterCode
        filterset_class = SubClusterCodeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('id')
            else:
                queryset = queryset.filter(status=True).order_by('id')
        except:
            queryset = queryset.filter(status=True).order_by('id')
        return queryset


class CategoryFilter(FilterSet):
    pk = django_filters.CharFilter(lookup_expr='exact')
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Category
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value) |
            Q(name__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(Q(translations__name__icontains=value, translations__language_code="en") | Q(name__icontains=value))
        return queryset


class CategoryTranslationNode(DjangoObjectType):
    class Meta:
        model = CategoryTranslation
        filter_fields = ['id']


class CategoryNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = Category
        filterset_class = CategoryFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
            else:
                queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        except:
            queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        return queryset


class SearchCCC(graphene.Union):
    class Meta:
        types = (FamilyCodeNode, ClusterCodeNode, SubClusterCodeNode, CategoryNode)


class CCCConnection(graphene.Connection):
    class Meta:
        node = SearchCCC

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return len(root.iterable)


class SponsorFilter(FilterSet):
    class Meta:
        model = Sponsor
        fields = {
            'id': ['exact'],
            'name': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )


class SponsorTranslationNode(DjangoObjectType):
    class Meta:
        model = SponsorTranslation
        filter_fields = ['id']


class SponsorNode(DjangoObjectType):
    class Meta:
        model = Sponsor
        filterset_class = SponsorFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset

    def resolve_image(self, info):
        return info.context.build_absolute_uri(self.image.url)


class ReasonFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Reason
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value) |
            Q(name__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class ReasonTranslationNode(DjangoObjectType):
    class Meta:
        model = ReasonTranslation
        filter_fields = ['id']


class ReasonNode(DjangoObjectType):
    class Meta:
        model = Reason
        filterset_class = ReasonFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('item_code'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('item_code'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('item_code'))
        return queryset


class LanguageFilter(FilterSet):
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Language
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        language_code = translation.get_language()
        queryset_translation = queryset.filter(translations__name__icontains=value, translations__language_code=language_code)
        return queryset_translation.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="en")
        return queryset


class LanguageTranslationNode(DjangoObjectType):
    class Meta:
        model = LanguageTranslation
        filter_fields = ['id']


class LanguageNode(DjangoObjectType):
    class Meta:
        model = Language
        filterset_class = LanguageFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class PromotionUserUsedFilter(FilterSet):
    isUsed = django_filters.BooleanFilter(method="filter_promotion_used")
    date_from = django_filters.DateTimeFilter(method="filter_date_used_from")
    date_to = django_filters.DateTimeFilter(method='filter_date_used_to')
    real_amount_from = django_filters.NumberFilter(method="filter_real_amount_from")
    real_amount_to = django_filters.NumberFilter(method='filter_real_amount_to')
    amount_after_discount_from = django_filters.NumberFilter(method="filter_amount_after_discount_from")
    amount_after_discount_to = django_filters.NumberFilter(method='filter_amount_after_discount_to')
    commission_from = django_filters.NumberFilter(method="filter_commission_from")
    commission_to = django_filters.NumberFilter(method='filter_commission_to')

    class Meta:
        model = PromotionUserUsed
        fields = {
            'id': ['exact'],
            'user_used': ['icontains'],
            'user_used_email': ['icontains'],
            'user_name': ['icontains'],
            'title': ['icontains'],
            'promotion__discount': ['gte', 'lte'],
            'promotion__name': ['icontains'],
            'promotion__description': ['icontains'],
            'promotion__user_given': ['icontains'],
            'promotion__valid_from': ['gte'],
            'promotion__valid_to': ['lte'],
            'promotion__visible': ['exact'],
            'promotion__apply_for_buyer': ['exact'],
            'promotion__apply_for_supplier': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('user_used', 'user_used'),
            ('user_used_email', 'user_used_email'),
            ('user_name', 'user_name'),
            ('title', 'title'),
            ('real_amount', 'real_amount'),
            ('amount_after_discount', 'amount_after_discount'),
            ('promotion__discount', 'discount'),
            ('promotion__name', 'name'),
            ('promotion__description', 'description'),
            ('promotion__valid_from', 'valid_from'),
            ('promotion__valid_to', 'valid_to'),
            ('promotion__visible', 'visible'),
            ('promotion__user_given', 'user_given'),
            ('promotion__user_given_email', 'user_given_email'),
            ('promotion__apply_for_buyer', 'apply_for_buyer'),
            ('promotion__apply_for_supplier', 'apply_for_supplier'),
            ('promotion__commission', 'commission'),
        )
    )

    def filter_commission_from(self, queryset, name, value):
        queryset = queryset.filter(promotion__commission__gte=value).distinct()
        return queryset

    def filter_commission_to(self, queryset, name, value):
        queryset = queryset.filter(promotion__commission__lte=value).distinct()
        return queryset

    def filter_amount_after_discount_from(self, queryset, name, value):
        queryset = queryset.filter(amount_after_discountt__gte=value).distinct()
        return queryset

    def filter_amount_after_discount_to(self, queryset, name, value):
        queryset = queryset.filter(amount_after_discount__lte=value).distinct()
        return queryset

    def filter_real_amount_from(self, queryset, name, value):
        queryset = queryset.filter(real_amount__gte=value).distinct()
        return queryset

    def filter_real_amount_to(self, queryset, name, value):
        queryset = queryset.filter(real_amount__lte=value).distinct()
        return queryset

    def filter_date_used_from(self, queryset, name, value):
        queryset = queryset.filter(date_used__gte=value).distinct()
        return queryset

    def filter_date_used_to(self, queryset, name, value):
        queryset = queryset.filter(date_used__lte=value).distinct()
        return queryset

    def filter_promotion_used(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                if value:
                    queryset = queryset.filter(title__isnull=False).exclude(title__exact='').distinct().order_by("-id")
                else:
                    queryset = queryset.filter(title__isnull=True).exclude(title__exact='').distinct().order_by("-id")
                return queryset
            else:
                raise Exception("Invalid token")
        except:
            raise Exception("Invalid token")


class PromotionUserUsedNode(DjangoObjectType):
    class Meta:
        model = PromotionUserUsed
        filterset_class = PromotionUserUsedFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset


class PromotionFilter(FilterSet):
    isUsed = django_filters.BooleanFilter(method="filter_promotion_used")
    date_from = django_filters.DateTimeFilter(method="filter_date_used_from")
    date_to = django_filters.DateTimeFilter(method='filter_date_used_to')
    real_amount_from = django_filters.NumberFilter(method="filter_real_amount_from")
    real_amount_to = django_filters.NumberFilter(method='filter_real_amount_to')
    amount_after_discount_from = django_filters.NumberFilter(method="filter_amount_after_discount_from")
    amount_after_discount_to = django_filters.NumberFilter(method='filter_amount_after_discount_to')
    commission_from = django_filters.NumberFilter(method="filter_commission_from")
    commission_to = django_filters.NumberFilter(method='filter_commission_to')
    apply_scope = django_filters.CharFilter(method="filter_by_scope")
    referral_code_checking = django_filters.CharFilter(method="filter_by_referral_code_checking")

    class Meta:
        model = Promotion
        fields = {
            'id': ['exact'],
            'description': ['icontains'],
            'discount': ['icontains'],
            'name': ['icontains'],
            'status': ['exact'],
            'apply_for_buyer': ['exact'],
            'apply_for_supplier': ['exact'],
            'apply_for_advertisement': ['exact'],
            'user_given': ['icontains'],
            'visible': ['exact'],
            'user_given_email': ['icontains'],
            'promotion_users__user_used': ['icontains'],
            'promotion_users__user_used_email': ['icontains'],
            'promotion_users__user_name': ['icontains'],
            'promotion_users__title': ['icontains'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('item_code', 'item_code'),
            ('status', 'status'),
            ('translations__description', 'description'),
            ('apply_for_buyer', 'apply_for_buyer'),
            ('apply_for_supplier', 'apply_for_supplier'),
            ('apply_for_advertisement', 'apply_for_advertisement'),
            ('user_given', 'user_given'),
            ('promotion_users__user_used', 'user_used'),
            ('visible', 'visible'),
            ('user_given_email', 'user_given_email'),
            ('promotion_users__user_used_email', 'user_used_email'),
            ('promotion_users__user_name', 'user_name'),
            ('promotion_users__title', 'title'),
            ('promotion_users__date_used', 'date_used'),
            ('promotion_users__real_amount', 'real_amount'),
            ('promotion_users__amount_after_discount', 'amount_after_discount'),
            ('commission', 'commission')
        )
    )

    def filter_commission_from(self, queryset, name, value):
        queryset = queryset.filter(commission__gte=value).distinct()
        return queryset

    def filter_commission_to(self, queryset, name, value):
        queryset = queryset.filter(commission__lte=value).distinct()
        return queryset

    def filter_amount_after_discount_from(self, queryset, name, value):
        queryset = queryset.filter(promotion_users__amount_after_discountt__gte=value).distinct()
        return queryset

    def filter_amount_after_discount_to(self, queryset, name, value):
        queryset = queryset.filter(promotion_users__amount_after_discount__lte=value).distinct()
        return queryset

    def filter_real_amount_from(self, queryset, name, value):
        queryset = queryset.filter(promotion_users__real_amount__gte=value).distinct()
        return queryset

    def filter_real_amount_to(self, queryset, name, value):
        queryset = queryset.filter(promotion_users__real_amount__lte=value).distinct()
        return queryset

    def filter_date_used_from(self, queryset, name, value):
        queryset = queryset.filter(promotion_users__date_used__gte=value).distinct()
        return queryset

    def filter_date_used_to(self, queryset, name, value):
        queryset = queryset.filter(promotion_users__date_used__lte=value).distinct()
        return queryset

    def filter_promotion_used(self, queryset, name, value):
        try:
            key = self.request.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                if value:
                    queryset = queryset.filter(promotion_users__title__isnull=False).exclude(promotion_users__title__exact='').distinct().order_by("id")
                else:
                    queryset = queryset.filter(promotion_users__title__isnull=True).exclude(promotion_users__title__exact='').distinct().order_by("id")
                return queryset
            else:
                raise Exception("Invalid token")
        except:
            raise Exception("Invalid token")

    def filter_by_scope(self, queryset, name, value):
        if value.lower() == "sicp":
            queryset = queryset.filter(apply_scope__in=[PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_SICP])
        if value.lower() == "profile_features":
            queryset = queryset.filter(apply_scope__in=[PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES])
        if value.lower() == "buyer":
            queryset = queryset.filter(apply_scope=PromotionApplyScope.FOR_BUYER)
        return queryset

    def filter_by_referral_code_checking(self, queryset, name, value):
        queryset = queryset.filter(name=value)
        return queryset


class PromotionTranslationNode(DjangoObjectType):
    class Meta:
        model = PromotionTranslation
        filter_fields = ['id']


class PromotionNode(DjangoObjectType):
    description_default = graphene.String()

    class Meta:
        model = Promotion
        filterset_class = PromotionFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_description(self, info):
        return self.translated.description

    def resolve_description_default(self, info):
        return self.description

    @classmethod
    def get_queryset(cls, queryset, info):

        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('-id')
            elif token.user.isBuyer():
                queryset = queryset.filter(
                    apply_scope=PromotionApplyScope.FOR_BUYER,
                    status=True,
                    visible=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
            elif token.user.isSupplier():
                queryset = queryset.filter(
                    apply_scope__in=[
                        PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE,
                        PromotionApplyScope.FOR_SUPPLIER_SICP,
                        PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES,
                        PromotionApplyScope.FOR_SUPPLIER
                    ],
                    status=True,
                    visible=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
            else:
                if hasattr(info, 'variable_values') and 'referralCodeChecking' in info.variable_values and len(info.variable_values['referralCodeChecking']) > 0:
                    queryset = queryset.filter(status=True).order_by('id')
                else:
                    queryset = queryset.filter(status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()).order_by('id')
        except:
            if hasattr(info, 'variable_values') and 'referralCodeChecking' in info.variable_values and len(info.variable_values['referralCodeChecking']) > 0:
                queryset = queryset.filter(status=True).order_by('id')
            else:
                queryset = queryset.filter(status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()).order_by('id')
        return queryset


class PromotionResults(graphene.ObjectType):
    promotion = graphene.Field(PromotionNode)

    def resolve_promotion(self, info):
        promotion_instance = Promotion.objects.filter(name=self.name, status=True, valid_to__gte=timezone.now()).first()
        if promotion_instance is not None:
            promotion = promotion_instance
        else:
            promotion = {}
        return promotion


class PromotionConectionResults(graphene.Connection):
    class Meta:
        node = PromotionResults


class SupplierListFilter(FilterSet):
    class Meta:
        model = SupplierList
        fields = {
            'id': ['exact'],
            'name': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(fields=('name', 'status'))


class SupplierListTranslationNode(DjangoObjectType):
    class Meta:
        model = SupplierListTranslation
        filter_fields = ['id']


class SupplierListNode(DjangoObjectType):
    class Meta:
        model = SupplierList
        filterset_class = SupplierListFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('name'))
            else:
                queryset = queryset.filter(status=True).order_by(Lower('name'))
        except:
            queryset = queryset.filter(status=True).order_by(Lower('name'))
        return queryset


class EmailListFilter(FilterSet):
    class Meta:
        model = EmailList
        fields = {
            'id': ['exact'],
            'email': ['icontains'],
            'country': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(fields=('email', 'country', 'status'))


class EmailListNode(DjangoObjectType):
    class Meta:
        model = EmailList
        filterset_class = EmailListFilter
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('id')
            else:
                queryset = queryset.filter(status=True).order_by('id')
        except:
            queryset = queryset.filter(status=True).order_by('id')
        return queryset


class ExchangeRateFilter(FilterSet):
    class Meta:
        model = ExchangeRate
        fields = {
            'id': ['exact'],
            'unit_of_measures_name': ['icontains'],
            'item_code': ['exact'],
            'exchange_rate': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(fields=('unit_of_measures_name', 'item_code', 'exchange_rate', 'status'))


class ExchangeRateNode(DjangoObjectType):
    class Meta:
        model = ExchangeRate
        interfaces = (CustomNode,)
        filterset_class = ExchangeRateFilter
        connection_class = ExtendedConnection


class CouponFilter(FilterSet):
    valid_from = django_filters.CharFilter(method='valid_from_filter')
    valid_to = django_filters.CharFilter(method='valid_to_filter')

    class Meta:
        model = Coupon
        fields = {
            'id': ['exact'],
            'coupon_program': ['icontains'],
            'description': ['icontains'],
            'commission': ['exact'],
            'note': ['icontains'],
            'email': ['icontains'],
            'full_name': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=('coupon_program', 'description', 'commission', 'note', 'email', 'full_name', 'status', 'valid_from', 'valid_to')
    )

    def valid_from_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%d')
        queryset = queryset.filter(valid_from__gte=value)
        return queryset

    def valid_to_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%d')
        queryset = queryset.filter(valid_to__lte=value)
        return queryset


class CouponNode(DjangoObjectType):
    class Meta:
        model = Coupon
        filterset_class = CouponFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by(Lower('coupon_program'))
            else:
                queryset = queryset.filter(status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()).order_by('id')
        except:
            queryset = queryset.filter(status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()).order_by('id')
        return queryset


class BankFilter(FilterSet):
    class Meta:
        model = Bank
        fields = {
            'id': ['exact'],
            'item_code': ['icontains'],
            'name': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(fields=('id', 'item_code', 'name', 'status'))


class BankNode(DjangoObjectType):
    class Meta:
        model = Bank
        filterset_class = BankFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by('id')
            else:
                queryset = queryset.filter(status=True).order_by('id')
        except:
            queryset = queryset.filter(status=True).order_by('id')
        return queryset



class VoucherFilter(FilterSet):
    pk = django_filters.CharFilter(lookup_expr='exact')
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = Voucher
        fields = {
            'id': ['exact'],
            'voucher_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('voucher_code', 'voucher_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value) |
            Q(name__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(Q(translations__name__icontains=value, translations__language_code="en") | Q(name__icontains=value))
        return queryset

class VoucherTranslationNode(DjangoObjectType):
    class Meta:
        model = VoucherTranslation
        filter_fields = ['id']

class VoucherNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = Voucher
        filterset_class = VoucherFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
            else:
                queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        except:
            queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        return queryset

class BuyerClubVoucherFilter(FilterSet):
    pk = django_filters.CharFilter(lookup_expr='exact')
    description = django_filters.CharFilter(method="fillter_by_description")
    description_vi = django_filters.CharFilter(method="fillter_by_description_vi")
    description_en = django_filters.CharFilter(method="fillter_by_description_en")

    class Meta:
        model = BuyerClubVoucher
        fields = {
            'id': ['exact'],
            'voucher_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('voucher_code', 'voucher_code'),
            ('status', 'status'),
            ('translations__description', 'description'),
        )
    )

    def fillter_by_description(self, queryset, description, value):
        queryset = queryset.filter(
            Q(translations__description__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_description_vi(self, queryset, description, value):
        queryset = queryset.filter(translations__description__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_description_en(self, queryset, description, value):
        queryset = queryset.filter(Q(translations__description__icontains=value, translations__language_code="en") | Q(description__icontains=value))
        return queryset

class BuyerClubBuyerClubVoucherTranslationNode(DjangoObjectType):
    class Meta:
        model = BuyerClubVoucherTranslation
        filter_fields = ['id']

class BuyerClubVoucherNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = BuyerClubVoucher
        filterset_class = BuyerClubVoucherFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_description(self, info):
        return self.translated.description

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
            else:
                queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        except:
            queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        return queryset

class WarrantyTermFilter(FilterSet):
    pk = django_filters.CharFilter(lookup_expr='exact')
    name = django_filters.CharFilter(method="fillter_by_name")
    name_vi = django_filters.CharFilter(method="fillter_by_name_vi")
    name_en = django_filters.CharFilter(method="fillter_by_name_en")

    class Meta:
        model = WarrantyTerm
        fields = {
            'id': ['exact'],
            'warranty_code': ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('warranty_code', 'warranty_code'),
            ('status', 'status'),
            ('translations__name', 'name'),
        )
    )

    def fillter_by_name(self, queryset, name, value):
        queryset = queryset.filter(
            Q(translations__name__icontains=value) |
            Q(name__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_name_vi(self, queryset, name, value):
        queryset = queryset.filter(translations__name__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_name_en(self, queryset, name, value):
        queryset = queryset.filter(Q(translations__name__icontains=value, translations__language_code="en") | Q(name__icontains=value))
        return queryset

class WarrantyTermTranslationNode(DjangoObjectType):
    class Meta:
        model = WarrantyTermTranslation
        filter_fields = ['id']

class WarrantyTermNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = WarrantyTerm
        filterset_class = WarrantyTermFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_name(self, info):
        return self.translated.name

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
            else:
                queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        except:
            queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        return queryset

class SetProductAdvertisementFilter(FilterSet):
    pk = django_filters.CharFilter(lookup_expr='exact')
    description = django_filters.CharFilter(method="fillter_by_description")
    description_vi = django_filters.CharFilter(method="fillter_by_description_vi")
    description_en = django_filters.CharFilter(method="fillter_by_description_en")

    class Meta:
        model = SetProductAdvertisement
        fields = {
            'id': ['exact'],
            "duration": ['icontains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('duration', 'duration'),
            ('status', 'status'),
            ('translations__description', 'description'),
        )
    )

    def fillter_by_description(self, queryset, description, value):
        queryset = queryset.filter(
            Q(translations__description__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_description_vi(self, queryset, description, value):
        queryset = queryset.filter(translations__description__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_description_en(self, queryset, description, value):
        queryset = queryset.filter(Q(translations__description__icontains=value, translations__language_code="en") | Q(description__icontains=value))
        return queryset

class SetProductAdvertisementTranslationNode(DjangoObjectType):
    class Meta:
        model = SetProductAdvertisementTranslation
        filter_fields = ['id']

class SetProductAdvertisementNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = SetProductAdvertisement
        filterset_class = SetProductAdvertisementFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_description(self, info):
        return self.translated.description

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
            else:
                queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        except:
            queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        return queryset


""" class GroupFilter(FilterSet):
    pk = django_filters.CharFilter(lookup_expr='exact')
    name = django_filters.CharFilter(method="fillter_by_name")

    class Meta:
        model = SetProductAdvertisement
        fields = {
            'id': ['exact'],
            'member': ['exact'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('duration', 'duration'),
            ('status', 'status'),
            ('translations__description', 'description'),
        )
    )

    def fillter_by_description(self, queryset, description, value):
        queryset = queryset.filter(
            Q(translations__description__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.distinct()

    def fillter_by_description_vi(self, queryset, description, value):
        queryset = queryset.filter(translations__description__icontains=value, translations__language_code="vi")
        return queryset

    def fillter_by_description_en(self, queryset, description, value):
        queryset = queryset.filter(Q(translations__description__icontains=value, translations__language_code="en") | Q(description__icontains=value))
        return queryset

class SetProductAdvertisementTranslationNode(DjangoObjectType):
    class Meta:
        model = SetProductAdvertisementTranslation
        filter_fields = ['id']

class SetProductAdvertisementNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')

    class Meta:
        model = SetProductAdvertisement
        filterset_class = SetProductAdvertisementFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_description(self, info):
        return self.translated.description

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
            else:
                queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        except:
            queryset = gql_optimizer.query(queryset.filter(status=True).order_by('id'), info)
        return queryset """
# -----------------------CREATE-----------------------


class ReasonLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class ReasonInput(graphene.InputObjectType):
    item_code = graphene.String(required=True)
    names = graphene.List(ReasonLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class ReasonCreate(graphene.Mutation):
    class Arguments:
        input = ReasonInput(required=True)

    status = graphene.Boolean()
    reason = graphene.Field(ReasonNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        reason = Reason.objects.create(item_code=input.item_code, name=input.names[0].name, status=input.status)
        for name in input.names:
            reason.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            reason.save()
        return ReasonCreate(status=True, reason=reason)


class LanguageLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class LanguageInput(graphene.InputObjectType):
    item_code = graphene.String(required=True)
    names = graphene.List(LanguageLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class LanguageCreate(graphene.Mutation):
    class Arguments:
        input = LanguageInput(required=True)

    status = graphene.Boolean()
    language = graphene.Field(LanguageNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        language = Language.objects.create(item_code=input.item_code, name=input.names[0].name, status=input.status)
        for name in input.names:
            language.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            language.save()
        return LanguageCreate(status=True, language=language)


class ClientFocusInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")
    status = graphene.Boolean(default_value=True)


class ClientFocusCreate(graphene.Mutation):
    class Arguments:
        input = ClientFocusInput(required=True)

    status = graphene.Boolean()
    input = graphene.Field(ClientFocusNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        client_focus = ClientFocus.objects.create(name=input.name, status=input.status)
        return ClientFocusCreate(status=True, client_focus=client_focus)


class IndustryLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class IndustryInput(graphene.InputObjectType):
    item_code = graphene.String(required=True)
    names = graphene.List(IndustryLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class IndustryCreate(graphene.Mutation):
    class Arguments:
        input = IndustryInput(required=True)

    status = graphene.Boolean()
    industry = graphene.Field(IndustryNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):

        if len(input.item_code) > 2:
            error = Error(code="MASTER_DATA_01", message=MasterDataError.MASTER_DATA_01)
            return IndustryCreate(status=False, error=error)

        industry = Industry(name=input.names[0].name, item_code=input.item_code, status=input.status)

        if len(industry.item_code) < 2:
            industry.item_code = '0' + industry.item_code
        industry.save()
        for name in input.names:
            industry.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            if name.language_code == "en":
                industry.name = name.name
        return IndustryCreate(status=True, industry=industry)


class IndustryClusterLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class IndustryClusterInput(graphene.InputObjectType):
    names = graphene.List(IndustryClusterLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    industry = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class IndustryClusterCreate(graphene.Mutation):
    class Arguments:
        input = IndustryClusterInput(required=True)

    status = graphene.Boolean()
    industry_cluster = graphene.Field(IndustryClusterNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        if len(input.item_code) != 3:
            error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
            return IndustryClusterCreate(status=False, error=error)

        industry_cluster = IndustryCluster.objects.create(
            name=input.names[0].name,
            item_code=input.item_code,
            industry_id=input.industry,
            status=input.status,
        )
        for name in input.names:
            industry_cluster.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            if name.language_code == "en":
                industry_cluster.name = name.name
        industry_cluster.save()
        return IndustryClusterCreate(status=True, industry_cluster=industry_cluster)


class IndustrySectorsLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class IndustrySectorsInput(graphene.InputObjectType):
    names = graphene.List(IndustrySectorsLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    industry_cluster = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class IndustrySectorsCreate(graphene.Mutation):
    class Arguments:
        input = IndustrySectorsInput(required=True)

    status = graphene.Boolean()
    industry_sector = graphene.Field(IndustrySectorsNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        if len(input.item_code) != 4:
            error = Error(code="MASTER_DATA_03", message=MasterDataError.MASTER_DATA_03)
            return IndustrySectorsCreate(status=False, error=error)
        industry_sector = IndustrySectors.objects.create(
            name=input.names[0].name,
            item_code=input.item_code,
            industry_cluster_id=input.industry_cluster,
            status=input.status,
        )
        for name in input.names:
            industry_sector.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            if name.language_code == "en":
                industry_sector.name = name.name
        industry_sector.save()
        return IndustrySectorsCreate(status=True, industry_sector=industry_sector)


class IndustrySubSectorsLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class IndustrySubSectorsInput(graphene.InputObjectType):
    names = graphene.List(IndustrySubSectorsLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    industry_sector = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class IndustrySubSectorsCreate(graphene.Mutation):
    class Arguments:
        input = IndustrySubSectorsInput(required=True)

    status = graphene.Boolean()
    industry_sub_sector = graphene.Field(IndustrySubSectorsNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):

        if len(input.item_code) != 5:
            error = Error(code="MASTER_DATA_04", message=MasterDataError.MASTER_DATA_04)
            return IndustrySubSectorsCreate(status=False, error=error)

        industry_sub_sector = IndustrySubSectors.objects.create(
            name=input.names[0].name,
            item_code=input.item_code,
            industry_sectors_id=input.industry_sector,
            status=input.status,
        )
        for name in input.names:
            industry_sub_sector.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            if name.language_code == "en":
                industry_sub_sector.name = name.name
        industry_sub_sector.save()
        return IndustrySubSectorsCreate(status=True, industry_sub_sector=industry_sub_sector)


class PromotionLanguageCodeInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class PromotionApplyScopeInput(graphene.Enum):
    FOR_BUYER = PromotionApplyScope.FOR_BUYER
    FOR_SUPPLIER_ALL_SCOPE = PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE
    FOR_SUPPLIER_PROFILE_FEATURES = PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES
    FOR_SUPPLIER_SICP = PromotionApplyScope.FOR_SUPPLIER_SICP
    FOR_SUPPLIER = PromotionApplyScope.FOR_SUPPLIER


class PromotionInput(graphene.InputObjectType):
    descriptions = graphene.List(PromotionLanguageCodeInput, required=True)
    name = graphene.String(required=True)
    discount = graphene.Float(required=True)
    valid_from = graphene.String(required=True)
    valid_to = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)
    apply_for_buyer = graphene.Boolean(default_value=False)
    apply_for_supplier = graphene.Boolean(default_value=False)
    apply_for_advertisement = graphene.Boolean(default_value=False)
    user_id = graphene.String()
    visible = graphene.Boolean(default_value=False)
    user_given_email = graphene.String()
    user_given = graphene.String()
    commission = graphene.Float()
    apply_scope = PromotionApplyScopeInput(required=True)


class PromotionCreate(graphene.Mutation):
    class Arguments:
        input = PromotionInput(required=True)

    status = graphene.Boolean()
    promotion = graphene.Field(PromotionNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        if input.discount <= 0 or input.discount > 100:
            error = Error(code="MASTER_DATA_05", message=MasterDataError.MASTER_DATA_05)
            return PromotionCreate(status=False, error=error)

        if Promotion.objects.filter(name=input.name):
            error = Error(code="MASTER_DATA_06", message=MasterDataError.MASTER_DATA_06)
            return PromotionCreate(status=False, error=error)

        if input.user_id is not None and input.user_id != ' ':
            user_instance = User.objects.filter(id=input.user_id).first()
            if user_instance is not None:
                promotion = Promotion.objects.create(
                    name=input.name,
                    description=input.descriptions[0].description,
                    discount=input.discount,
                    valid_from=input.valid_from,
                    valid_to=input.valid_to,
                    status=input.status,
                    apply_for_buyer=input.apply_for_buyer,
                    apply_for_supplier=input.apply_for_supplier,
                    apply_for_advertisement=input.apply_for_advertisement,
                    visible=input.visible,
                    user_given=user_instance.username,
                    user_given_email=input.user_given_email,
                    commission=input.commission,
                    apply_scope=input.apply_scope
                )
            else:
                raise Exception("User does not exist")
        else:
            promotion = Promotion.objects.create(
                name=input.name,
                description=input.descriptions[0].description,
                discount=input.discount,
                valid_from=input.valid_from,
                valid_to=input.valid_to,
                status=input.status,
                apply_for_buyer=input.apply_for_buyer,
                apply_for_supplier=input.apply_for_supplier,
                apply_for_advertisement=input.apply_for_advertisement,
                visible=input.visible,
                user_given_email=input.user_given_email,
                user_given=input.user_given,
                commission=input.commission,
                apply_scope=input.apply_scope
            )
        for description in input.descriptions:
            promotion.translations.update_or_create(language_code=description.language_code, defaults={'description': description.description})
            promotion.save()
        if promotion.apply_scope == PromotionApplyScope.FOR_BUYER:
            promotion.apply_for_buyer = True
            promotion.apply_for_supplier = False
        else:
            promotion.apply_for_buyer = False
            promotion.apply_for_supplier = True
        promotion.save()
        return PromotionCreate(status=True, promotion=promotion)


class CountryLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class CountryInput(graphene.InputObjectType):
    item_code = graphene.String(required=True)
    names = graphene.List(CountryLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class CountryCreate(graphene.Mutation):
    class Arguments:
        input = CountryInput(required=True)

    status = graphene.Boolean()
    country = graphene.Field(CountryNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        country = Country.objects.create(item_code=input.item_code, name=input.names[0].name, status=input.status)
        for name in input.names:
            country.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            country.save()
        return CountryCreate(status=True, country=country)


class CountryStateLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class CountryStateInput(graphene.InputObjectType):
    item_code = graphene.String(required=True)
    names = graphene.List(CountryStateLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)
    country = graphene.String(required=True)


class CountryStateCreate(graphene.Mutation):
    class Arguments:
        input = CountryStateInput(required=True)

    status = graphene.Boolean()
    country_state = graphene.Field(CountryStateNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            user = GetToken.getToken(info).user
            if user.isAdmin():
                if not Country.objects.filter(pk=input.country, status=True).exists():
                    error = Error(code="MASTER_DATA_16", message=MasterDataError.MASTER_DATA_16)
                    return CountryStateCreate(status=False, error=error)

                if CountryState.objects.filter(state_code=input.item_code, country_id=input.country).exists():
                    error = Error(code="MASTER_DATA_13", message=MasterDataError.MASTER_DATA_13)
                    return CountryStateCreate(status=False, error=error)

                country_state = CountryState.objects.create(state_code=input.item_code, name=input.names[0].name, status=input.status, country_id=input.country)
                for name in input.names:
                    country_state.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
                    country_state.save()
                return CountryStateCreate(status=True, country_state=country_state)
            else:
                error = Error(code="MASTER_DATA_14", message=MasterDataError.MASTER_DATA_14)
                return CountryStateCreate(status=False, error=error)
        except:
            raise Exception('you must be logged in')


class CurrencyLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class CurrencyInput(graphene.InputObjectType):
    names = graphene.List(CurrencyLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class CurrencyCreate(graphene.Mutation):
    class Arguments:
        input = CurrencyInput(required=True)

    status = graphene.Boolean()
    currency = graphene.Field(CurrencyNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        currency = Currency.objects.create(item_code=input.item_code, name=input.names[0].name, status=input.status)
        for name in input.names:
            currency.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            currency.save()
        return CurrencyCreate(status=True, currency=currency)


class ContractTypeLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class ContractTypeInput(graphene.InputObjectType):
    names = graphene.List(ContractTypeLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class ContractTypeCreate(graphene.Mutation):
    class Arguments:
        input = ContractTypeInput(required=True)

    status = graphene.Boolean()
    contract_type = graphene.Field(ContractTypeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        contract_type = ContractType.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            contract_type.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            contract_type.save()
        return ContractTypeCreate(status=True, contract_type=contract_type)


class PaymentTermLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class PaymentTermInput(graphene.InputObjectType):
    names = graphene.List(PaymentTermLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class PaymentTermCreate(graphene.Mutation):
    class Arguments:
        input = PaymentTermInput(required=True)

    status = graphene.Boolean()
    payment_term = graphene.Field(PaymentTermNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        payment_term = PaymentTerm.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            payment_term.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            if (name.language_code == "en"):
                payment_term.name = name.name
            payment_term.save()
        return PaymentTermCreate(status=True, payment_term=payment_term)


class DeliveryTermLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class DeliveryTermInput(graphene.InputObjectType):
    names = graphene.List(DeliveryTermLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class DeliveryTermCreate(graphene.Mutation):
    class Arguments:
        input = DeliveryTermInput(required=True)

    status = graphene.Boolean()
    delivery_term = graphene.Field(DeliveryTermNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        delivery_term = DeliveryTerm.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            delivery_term.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            delivery_term.save()
        return DeliveryTermCreate(status=True, delivery_term=delivery_term)


class UnitofMeasureLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class UnitofMeasureInput(graphene.InputObjectType):
    names = graphene.List(UnitofMeasureLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class UnitofMeasureCreate(graphene.Mutation):
    class Arguments:
        input = UnitofMeasureInput(required=True)

    status = graphene.Boolean()
    unit_of_measure = graphene.Field(UnitofMeasureNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        unit_of_measure = UnitofMeasure.objects.create(item_code=input.item_code, name=input.names[0].name, status=input.status)
        for name in input.names:
            unit_of_measure.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            if name.language_code == 'en':
                unit_of_measure.name = name.name
        unit_of_measure.save()
        return UnitofMeasureCreate(status=True, unit_of_measure=unit_of_measure)


class EmailTemplatesLanguageCodeInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class EmailTemplatesInput(graphene.InputObjectType):
    email_templates_languages = graphene.List(EmailTemplatesLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    variables = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class EmailTemplatesCreate(graphene.Mutation):
    class Arguments:
        input = EmailTemplatesInput(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)
    email_templates = graphene.Field(EmailTemplatesNode)

    def mutate(root, info, input):
        email_templates = EmailTemplates.objects.create(
            item_code=input.item_code,
            title=input.email_templates_languages[0].title,
            content=input.email_templates_languages[0].content,
            variables=input.variables,
            status=input.status,
        )
        for email_templates_language in input.email_templates_languages:
            email_templates.translations.update_or_create(
                language_code=email_templates_language.language_code,
                defaults={'title': email_templates_language.title, 'content': email_templates_language.content},
            )
            email_templates.save()
        return EmailTemplatesCreate(status=True, email_templates=email_templates)


class NumberofEmployeeLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class NumberofEmployeeInput(graphene.InputObjectType):
    names = graphene.List(NumberofEmployeeLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class NumberofEmployeeCreate(graphene.Mutation):
    class Arguments:
        input = NumberofEmployeeInput(required=True)

    status = graphene.Boolean()
    number_of_employee = graphene.Field(NumberofEmployeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        number_of_employee = NumberofEmployee.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            number_of_employee.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            number_of_employee.save()
        return NumberofEmployeeCreate(status=True, number_of_employee=number_of_employee)


class GenderLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class GenderInput(graphene.InputObjectType):
    names = graphene.List(GenderLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class GenderCreate(graphene.Mutation):
    class Arguments:
        input = GenderInput(required=True)

    status = graphene.Boolean()
    gender = graphene.Field(GenderNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        gender = Gender.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            gender.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            gender.save()
        return GenderCreate(status=True, gender=gender)


class TechnicalWeightingLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class TechnicalWeightingInput(graphene.InputObjectType):
    names = graphene.List(TechnicalWeightingLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class TechnicalWeightingCreate(graphene.Mutation):
    class Arguments:
        input = TechnicalWeightingInput(required=True)

    status = graphene.Boolean()
    technical_weighting = graphene.Field(TechnicalWeightingNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        technical_weighting = TechnicalWeighting.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            technical_weighting.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            technical_weighting.save()
        return TechnicalWeightingCreate(status=True, technical_weighting=technical_weighting)


class AuctionTypeLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class AuctionTypeInput(graphene.InputObjectType):
    names = graphene.List(AuctionTypeLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class AuctionTypeCreate(graphene.Mutation):
    class Arguments:
        input = AuctionTypeInput(required=True)

    status = graphene.Boolean()
    auction_type = graphene.Field(AuctionTypeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        auction_type = AuctionType.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            auction_type.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            auction_type.save()
        return AuctionTypeCreate(status=True, auction_type=auction_type)


class PositionLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class PositionInput(graphene.InputObjectType):
    names = graphene.List(PositionLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class PositionCreate(graphene.Mutation):
    class Arguments:
        input = PositionInput(required=True)

    status = graphene.Boolean()
    position = graphene.Field(PositionNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        position = Position.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            position.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            position.save()
        return PositionCreate(status=True, position=position)


class LevelLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class LevelInput(graphene.InputObjectType):
    names = graphene.List(LevelLanguageCodeInput, required=True)
    status = graphene.Boolean(default_value=True)


class LevelCreate(graphene.Mutation):
    class Arguments:
        input = LevelInput(required=True)

    status = graphene.Boolean()
    level = graphene.Field(LevelNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        level = Level.objects.create(name=input.names[0].name, status=input.status)
        for name in input.names:
            level.translations.update_or_create(language_code=level.language_code, defaults={'name': level.name})
            level.save()
        return LevelCreate(status=True, level=level)


class FamilyCodeLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class FamilyCodeInput(graphene.InputObjectType):
    names = graphene.List(FamilyCodeLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class FamilyCodeCreate(graphene.Mutation):
    class Arguments:
        input = FamilyCodeInput(required=True)

    status = graphene.Boolean()
    family_code = graphene.Field(FamilyCodeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):

        if len(input.item_code) >= 3:
            error = Error(code="MASTER_DATA_01", message=MasterDataError.MASTER_DATA_01)
            return FamilyCodeCreate(status=False, error=error)
        family_code = FamilyCode(item_code=input.item_code, name=input.names[0].name, status=input.status)
        for name in input.names:
            if name.language_code == 'en':
                family_code.name = name.name

        if len(family_code.item_code) < 2:
            family_code.item_code = '0' + family_code.item_code
        family_code.save()
        for name in input.names:
            family_code.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            family_code.save()

        return FamilyCodeCreate(status=True, family_code=family_code)


class ClusterCodeLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class ClusterCodeInput(graphene.InputObjectType):
    names = graphene.List(ClusterCodeLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    family_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class ClusterCodeCreate(graphene.Mutation):
    class Arguments:
        input = ClusterCodeInput(required=True)

    status = graphene.Boolean()
    cluster_code = graphene.Field(ClusterCodeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):

        if len(input.item_code) >= 4:
            error = Error(code="MASTER_DATA_07", message=MasterDataError.MASTER_DATA_07)
            return ClusterCodeCreate(status=False, error=error)

        cluster_code = ClusterCode(
            item_code=input.item_code,
            name=input.names[0].name,
            family_code_id=input.family_code,
            status=input.status,
        )
        for name in input.names:
            if name.language_code == 'en':
                cluster_code.name = name.name

        if len(cluster_code.item_code) < 2:
            cluster_code.item_code = '0' + cluster_code.item_code
        cluster_code.save()
        for name in input.names:
            cluster_code.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            cluster_code.save()

        return ClusterCodeCreate(status=True, cluster_code=cluster_code)


class SubClusterCodeLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class SubClusterCodeInput(graphene.InputObjectType):
    names = graphene.List(SubClusterCodeLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    cluster_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class SubClusterCodeCreate(graphene.Mutation):
    class Arguments:
        input = SubClusterCodeInput(required=True)

    status = graphene.Boolean()
    sub_cluster_code = graphene.Field(SubClusterCodeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):

        if len(input.item_code) >= 5:
            error = Error(code="MASTER_DATA_08", message=MasterDataError.MASTER_DATA_08)
            return SubClusterCodeCreate(status=False, error=error)

        sub_cluster_code = SubClusterCode(
            item_code=input.item_code,
            name=input.names[0].name,
            cluster_code_id=input.cluster_code,
            status=input.status,
        )
        for name in input.names:
            if name.language_code == 'en':
                sub_cluster_code.name = name.name

        if len(sub_cluster_code.item_code) < 2:
            sub_cluster_code.item_code = '0' + sub_cluster_code.item_code
        sub_cluster_code.save()
        for name in input.names:
            sub_cluster_code.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            sub_cluster_code.save()

        return SubClusterCodeCreate(status=True, sub_cluster_code=sub_cluster_code)


class CategoryLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class CategoryInput(graphene.InputObjectType):
    names = graphene.List(CategoryLanguageCodeInput, required=True)
    item_code = graphene.String(required=True)
    sub_cluster_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class CategoryCreate(graphene.Mutation):
    class Arguments:
        input = CategoryInput(required=True)

    status = graphene.Boolean()
    category = graphene.Field(SubClusterCodeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):

        if len(input.item_code) >= 6:
            error = Error(code="MASTER_DATA_09", message=MasterDataError.MASTER_DATA_09)
            return CategoryCreate(status=False, error=error)

        category = Category(
            item_code=input.item_code, name=input.names[0].name, sub_cluster_code_id=input.sub_cluster_code, status=input.status
        )
        for name in input.names:
            if name.language_code == 'en':
                category.name = name.name

        if len(category.item_code) < 2:
            category.item_code = '0' + category.item_code
        category.save()
        for name in input.names:
            category.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
            category.save()
        return CategoryCreate(status=True, category=category)

class SupplierListInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    status = graphene.Boolean()


class SupplierListCreate(graphene.Mutation):
    class Arguments:
        supplier_list = SupplierListInput(required=True)

    status = graphene.Boolean()
    supplier_list = graphene.Field(SupplierListNode)
    error = graphene.Field(Error)

    def mutate(root, info, supplier_list):
        supplier_list_instance = SupplierList(name=supplier_list.name, status=supplier_list.status)
        supplier_list_instance.save()
        return SupplierListCreate(status=True, supplier_list=supplier_list_instance)


class EmailListInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    country = graphene.String(required=True)
    status = graphene.Boolean()


class EmailListCreate(graphene.Mutation):
    class Arguments:
        email_list = EmailListInput(required=True)

    status = graphene.Boolean()
    email_list = graphene.Field(EmailListNode)
    error = graphene.Field(Error)

    def mutate(root, info, email_list):
        email_list_instance = EmailList(email=email_list.email, country=email_list.country, status=email_list.status)
        email_list_instance.save()
        return EmailListCreate(status=True, email_list=email_list_instance)


class ExchangeRateInput(graphene.InputObjectType):
    unit_of_measures_name = graphene.String(required=True)
    item_code = graphene.String(required=True)
    exchange_rate = graphene.Float(required=True)
    status = graphene.Boolean()


class ExchangeRateCreate(graphene.Mutation):
    class Arguments:
        exchange_rate = ExchangeRateInput(required=True)

    status = graphene.Boolean()
    exchange_rate = graphene.Field(ExchangeRateNode)

    def mutate(root, info, exchange_rate=None):
        exchange_rate_instance = ExchangeRate(
            unit_of_measures_name=exchange_rate.unit_of_measures_name,
            item_code=exchange_rate.item_code,
            exchange_rate=exchange_rate.exchange_rate,
            status=exchange_rate.status,
        )
        exchange_rate_instance.save()
        return ExchangeRateCreate(status=True, exchange_rate=exchange_rate_instance)


class CouponInput(graphene.InputObjectType):
    coupon_program = graphene.String(required=True)
    description = graphene.String(required=True)
    commission = graphene.Float(required=True)
    valid_from = graphene.String(required=True)
    valid_to = graphene.String(required=True)
    email = graphene.String(required=True)
    full_name = graphene.String(required=True)
    note = graphene.String(required=True)
    status = graphene.Boolean()


class CouponCreate(graphene.Mutation):
    class Arguments:
        coupon = CouponInput(required=True)

    status = graphene.Boolean()
    coupon = graphene.Field(CouponNode)
    error = graphene.Field(Error)

    def mutate(root, info, coupon):

        if coupon.commission <= 0 or coupon.commission > 100:
            error = Error(code="MASTER_DATA_10", message=MasterDataError.MASTER_DATA_10)
            return CouponCreate(status=False, error=error)

        if Coupon.objects.filter(coupon_program=coupon.coupon_program):
            error = Error(code="MASTER_DATA_11", message=MasterDataError.MASTER_DATA_11)
            return CouponCreate(status=False, error=error)

        if coupon.valid_from > coupon.valid_to:
            error = Error(code="MASTER_DATA_12", message=MasterDataError.MASTER_DATA_12)
            return CouponCreate(status=False, error=error)

        coupon_instance = Coupon(
            coupon_program=coupon.coupon_program,
            description=coupon.description,
            commission=coupon.commission,
            valid_from=coupon.valid_from,
            valid_to=coupon.valid_to,
            note=coupon.note,
            email=coupon.email,
            full_name=coupon.full_name,
            status=coupon.status,
        )
        coupon_instance.save()
        return CouponCreate(status=True, coupon=coupon_instance)


class BankInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    item_code = graphene.String(required=True)


class BankCreate(graphene.Mutation):
    class Arguments:
        bank = BankInput(required=True)

    status = graphene.Boolean()
    bank = graphene.Field(BankNode)
    error = graphene.Field(Error)

    def mutate(root, info, bank):
        if Bank.objects.filter(item_code=bank.item_code):
            error = Error(code="MASTER_DATA_13", message=MasterDataError.MASTER_DATA_13)
            return BankCreate(status=False, error=error)

        bank = Bank.objects.create(name=bank.name, item_code=bank.item_code)

        return BankCreate(status=True, bank=bank)

class VoucherLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")

class VoucherInput(graphene.InputObjectType):
    names = graphene.List(VoucherLanguageCodeInput, required=True)
    voucher_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)
    discount = graphene.Int(default_value=0, min=0, max=100)
    label = graphene.String(default_value='')


class VoucherCreate(graphene.Mutation):
    class Arguments:
        input = VoucherInput(required=True)

    status = graphene.Boolean()
    voucher = graphene.Field(VoucherNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            if len(input.voucher_code) != 3:
                error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
                return VoucherCreate(status=False, error=error)
            if input.discount < 0 or input.discount > 100:
                error = Error(code="MASTER_DATA_00", message='discount is not in range {}-{}'.format(0,100))
                return VoucherCreate(status=False, error=error)

            voucher = Voucher(
                voucher_code=input.voucher_code, 
                discount=input.discount, 
                status=input.status, 
                label = input.label,
            )

            for name in input.names:
                if name.language_code == 'en':
                    voucher.name = name.name
            voucher.save()

            for name in input.names:
                voucher.translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
                voucher.save()
            return VoucherCreate(status=True, voucher=voucher)
        except Exception as err:
            transaction.set_rollback(True)
            return VoucherCreate(status=False,error=err)

class BuyerClubVoucherLanguageCodeInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    language_code = graphene.String(default_value="en")

class BuyerClubVoucherInput(graphene.InputObjectType):
    descriptions = graphene.List(BuyerClubVoucherLanguageCodeInput, required=True)
    voucher_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)
    standard = graphene.Int(default_value=0, min=0, max=100)
    gold = graphene.Int(default_value=0, min=0, max=100)
    platinum = graphene.Int(default_value=0, min=0, max=100)
    diamond = graphene.Int(default_value=0, min=0, max=100)
    label = graphene.String(default_value='')


class BuyerClubVoucherCreate(graphene.Mutation):
    class Arguments:
        input = BuyerClubVoucherInput(required=True)

    status = graphene.Boolean()
    buyer_club_voucher = graphene.Field(BuyerClubVoucherNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            if len(input.voucher_code) != 3:
                error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
                return BuyerClubVoucherCreate(status=False, error=error)

            buyer_club_voucher = BuyerClubVoucher(
                voucher_code=input.voucher_code, 
                status=input.status, 
                label = input.label,
                standard = input.standard,
                gold = input.gold,
                platinum = input.platinum,
                diamond = input.diamond,
            )

            for description in input.descriptions:
                if description.language_code == 'en':
                    buyer_club_voucher.description = description.description
            buyer_club_voucher.save()

            for description in input.descriptions:
                buyer_club_voucher.translations.update_or_create(language_code=description.language_code, defaults={'description': description.description})
                buyer_club_voucher.save()
            return BuyerClubVoucherCreate(status=True, buyer_club_voucher=buyer_club_voucher)
        except Exception as err:
            transaction.set_rollback(True)
            return BuyerClubVoucherCreate(status=False,error=err)


class WarrantyTermLanguageCodeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")

class WarrantyTermInput(graphene.InputObjectType):
    names = graphene.List(WarrantyTermLanguageCodeInput, required=True)
    warranty_code = graphene.String(required=True)
    status = graphene.Boolean(default_value=True)


class WarrantyTermCreate(graphene.Mutation):
    class Arguments:
        input = WarrantyTermInput(required=True)

    status = graphene.Boolean()
    warranty_term = graphene.Field(WarrantyTermNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            if len(input.warranty_code) != 3:
                error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
                return WarrantyTermCreate(status=False, error=error)
    
            warranty_term  = WarrantyTerm(
                warranty_code=input.warranty_code, 
                status=input.status, 
            )

            for name in input.names:
                if name.language_code == 'en':
                    warranty_term.name = name.name
            warranty_term.save()

            for name in input.names:
                warranty_term .translations.update_or_create(language_code=name.language_code, defaults={'name': name.name})
                warranty_term .save()
            return WarrantyTermCreate(status=True, warranty_term =warranty_term )
        except Exception as err:
            transaction.set_rollback(True)
            return WarrantyTermCreate(status=False,error=err)

class SetProductAdvertisementLanguageCodeInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    language_code = graphene.String(default_value="en")

class SetProductAdvertisementInput(graphene.InputObjectType):
    descriptions = graphene.List(SetProductAdvertisementLanguageCodeInput, required=True)
    duration = graphene.Int(required=True)
    serviceFee = graphene.Int(required=True)
    status = graphene.Boolean(default_value=True)


class SetProductAdvertisementCreate(graphene.Mutation):
    class Arguments:
        input = SetProductAdvertisementInput(required=True)

    status = graphene.Boolean()
    set_product_advertisement = graphene.Field(SetProductAdvertisementNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            if input.duration < 1 or input.duration > 365:
                error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
                return SetProductAdvertisementCreate(status=False, error=error)

            set_product_advertisement  = SetProductAdvertisement(
                duration=input.duration, 
                serviceFee=input.serviceFee, 
                status=input.status, 
            )

            for description in input.descriptions:
                if description.language_code == 'en':
                    set_product_advertisement.description = description.description
            set_product_advertisement.save()

            for description in input.descriptions:
                 set_product_advertisement .translations.update_or_create(language_code=description.language_code, defaults={'description': description.description})
                 set_product_advertisement.save()
            return SetProductAdvertisementCreate(status=True, set_product_advertisement =set_product_advertisement )
        except Exception as err:
            transaction.set_rollback(True)
            return SetProductAdvertisementCreate(status=False,error=err)

# --------------------UPDATE----------------------


class ReasonUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ReasonInput(required=True)

    status = graphene.Boolean()
    reason = graphene.Field(ReasonNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        reason = Reason.objects.get(pk=id)
        if reason:
            reason.item_code = input.item_code
            reason.status = input.status
            reason.name = input.names[0].name
            reason.save()
            for name in input.names:
                reason.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                reason.save()
            return ReasonUpdate(status=True, reason=reason)
        return ReasonUpdate(status=False)


class ReasonStatusInput(graphene.InputObjectType):
    reason_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class ReasonUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(ReasonStatusInput, required=True)

    def mutate(root, info, list_status):
        for reason_status in list_status:
            reason = Reason.objects.get(id=reason_status.reason_id)
            reason.status = reason_status.status
            reason.save()
        return ReasonUpdateStatus(status=True)


class LanguageUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = LanguageInput(required=True)

    status = graphene.Boolean()
    language = graphene.Field(LanguageNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        language = Language.objects.get(pk=id)
        if language:
            language.item_code = input.item_code
            language.status = input.status
            language.name = input.names[0].name
            language.save()
            for name in input.names:
                language.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                language.save()
            return LanguageUpdate(status=True, language=language)
        return LanguageUpdate(status=False, error=None)


class LanguageStatusInput(graphene.InputObjectType):
    language_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class LanguageUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(LanguageStatusInput, required=True)

    def mutate(root, info, list_status):
        for language_status in list_status:
            language = Language.objects.get(id=language_status.language_id)
            language.status = language_status.status
            language.save()
        return LanguageUpdateStatus(status=True)


class ClientFocusUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ClientFocusInput(required=True)

    status = graphene.Boolean()
    client_focus = graphene.Field(ClientFocusNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        client_focus = ClientFocus.objects.get(pk=id)
        if client_focus:
            client_focus.status = input.status
            client_focus.name = input.name
            client_focus.translations.update_or_create(language_code=input.language_code, defaults={"name": input.name})
            client_focus.save()
            return ClientFocusUpdate(status=True, client_focus=client_focus)
        return ClientFocusUpdate(status=False, error=None)


class ClientFocusStatusInput(graphene.InputObjectType):
    client_focus_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class ClientFocusUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(ClientFocusStatusInput, required=True)

    def mutate(root, info, list_status):
        for client_focus_status in list_status:
            client_focus = ClientFocus.objects.get(id=client_focus_status.client_focus_id)
            client_focus.status = client_focus_status.status
            client_focus.save()
        return ClientFocusUpdateStatus(status=True)


class IndustryUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = IndustryInput(required=True)

    status = graphene.Boolean()
    industry = graphene.Field(IndustryNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        industry = Industry.objects.get(pk=id)

        if len(input.item_code) >= 3:
            error = Error(code="MASTER_DATA_01", message=MasterDataError.MASTER_DATA_01)
            return IndustryUpdate(status=False, error=error)

        if industry:
            industry.item_code = input.item_code
            industry.status = input.status
            industry.name = input.names[0].name
            if len(industry.item_code) < 2:
                industry.item_code = '0' + industry.item_code
            industry.save()
            for name in input.names:
                industry.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                if name.language_code == "en":
                    industry.name = name.name
                industry.save()
            return IndustryUpdate(status=True, industry=industry)
        return IndustryUpdate(status=False, error=None)


class IndustryStatusInput(graphene.InputObjectType):
    industry_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class IndustryUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(IndustryStatusInput, required=True)

    def mutate(root, info, list_status):
        for industry_status in list_status:
            industry = Industry.objects.get(id=industry_status.industry_id)
            industry.status = industry_status.status
            industry.save()
        return IndustryUpdateStatus(status=True)


class IndustryClusterUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = IndustryClusterInput(required=True)

    status = graphene.Boolean()
    industry_cluster = graphene.Field(IndustryClusterNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        industry_cluster = IndustryCluster.objects.get(pk=id)
        if len(input.item_code) != 3:
            error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
            return IndustryClusterUpdate(status=False, error=error)

        if industry_cluster:
            industry_cluster.item_code = input.item_code
            industry_cluster.status = input.status
            industry_cluster.name = input.names[0].name
            industry_cluster.save()
            for name in input.names:
                industry_cluster.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                industry_cluster.save()
            return IndustryClusterUpdate(status=True, industry_cluster=industry_cluster)
        return IndustryClusterUpdate(status=False, error=None)


class IndustryClusterStatusInput(graphene.InputObjectType):
    industry_cluster_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class IndustryClusterUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(IndustryClusterStatusInput, required=True)

    def mutate(root, info, list_status):
        for industry_cluster_status in list_status:
            industry_cluster = IndustryCluster.objects.get(id=industry_cluster_status.industry_cluster_id)
            industry_cluster.status = industry_cluster_status.status
            industry_cluster.save()
        return IndustryClusterUpdateStatus(status=True)


class IndustrySectorsUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = IndustrySectorsInput(required=True)

    status = graphene.Boolean()
    industry_sector = graphene.Field(IndustrySectorsNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        industry_sector = IndustrySectors.objects.get(pk=id)

        if len(input.item_code) != 4:
            error = Error(code="MASTER_DATA_03", message=MasterDataError.MASTER_DATA_03)
            return IndustrySectorsUpdate(status=False, error=error)

        if industry_sector:
            industry_sector.item_code = input.item_code
            industry_sector.status = input.status
            industry_sector.name = input.names[0].name
            industry_sector.save()
            for name in input.names:
                industry_sector.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                industry_sector.save()
            return IndustrySectorsUpdate(status=True, industry_sector=industry_sector)
        return IndustrySectorsUpdate(status=False, industry_sector=None)


class IndustrySectorsStatusInput(graphene.InputObjectType):
    industry_sectors_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class IndustrySectorsUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(IndustrySectorsStatusInput, required=True)

    def mutate(root, info, list_status):
        for industry_sectors_status in list_status:
            industry_sectors = IndustrySectors.objects.get(id=industry_sectors_status.industry_sectors_id)
            industry_sectors.status = industry_sectors_status.status
            industry_sectors.save()
        return IndustrySectorsUpdateStatus(status=True)


class IndustrySubSectorsUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = IndustrySubSectorsInput(required=True)

    status = graphene.Boolean()
    industry_sub_sector = graphene.Field(IndustrySubSectorsNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        industry_sub_sector = IndustrySubSectors.objects.get(pk=id)

        if len(input.item_code) != 5:
            error = Error(code="MASTER_DATA_04", message=MasterDataError.MASTER_DATA_04)
            return IndustrySubSectorsUpdate(status=False, error=error)
        if industry_sub_sector:
            industry_sub_sector.item_code = input.item_code
            industry_sub_sector.name = input.names[0].name
            industry_sub_sector.status = input.status
            industry_sub_sector.save()

            for name in input.names:
                industry_sub_sector.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                industry_sub_sector.save()

            return IndustrySubSectorsUpdate(status=True, industry_sub_sector=industry_sub_sector)
        return IndustrySubSectorsUpdate(status=False, industry_sub_sector=None)


class IndustrySubSectorsStatusInput(graphene.InputObjectType):
    industry_sub_sectors_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class IndustrySubSectorsUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(IndustrySubSectorsStatusInput, required=True)

    def mutate(root, info, list_status):
        for industry_sub_sectors_status in list_status:
            industry_sub_sectors = IndustrySubSectors.objects.get(id=industry_sub_sectors_status.industry_sub_sectors_id)
            industry_sub_sectors.status = industry_sub_sectors_status.status
            industry_sub_sectors.save()
        return IndustrySubSectorsUpdateStatus(status=True)


class PromotionUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = PromotionInput(required=True)

    status = graphene.Boolean()
    promotion = graphene.Field(PromotionNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        if input.discount <= 0 or input.discount > 100:
            error = Error(code="MASTER_DATA_05", message=MasterDataError.MASTER_DATA_05)
            return PromotionUpdate(status=False, error=error)
        promotion = Promotion.objects.get(pk=id)
        if promotion:
            user_given = promotion.user_given
            promotion.name = input.name
            if input.user_id is not None:
                user_instance = User.objects.filter(id=input.user_id).first()
                user_given = user_instance.username
            elif 'user_given' in input and input.user_given is not None:
                user_given = input.user_given
            if Promotion.objects.filter(name=input.name).exclude(id=promotion.id):
                raise GraphQLError('Promotion Program is already exists')

            for key, values in input.items():
                if key in [f.name for f in Promotion._meta.get_fields()]:
                    setattr(promotion, key, values)
            promotion.user_given = user_given
            if promotion.apply_scope == PromotionApplyScope.FOR_BUYER:
                promotion.apply_for_buyer = True
                promotion.apply_for_supplier = False
            else:
                promotion.apply_for_buyer = False
                promotion.apply_for_supplier = True
            promotion.save()

            for description in input.descriptions:
                promotion.translations.update_or_create(language_code=description.language_code, defaults={"description": description.description})
                promotion.save()

            return PromotionUpdate(status=True, promotion=promotion)
        return PromotionUpdate(status=False, promotion=None)


class PromotionStatusInput(graphene.InputObjectType):
    promotion_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class PromotionUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(PromotionStatusInput, required=True)

    def mutate(root, info, list_status):
        for promotion_status in list_status:
            promotion = Promotion.objects.get(id=promotion_status.promotion_id)
            promotion.status = promotion_status.status
            promotion.save()
        return PromotionUpdateStatus(status=True)


class PromotionVisibleInput(graphene.InputObjectType):
    promotion_id = graphene.String(required=True)
    visible = graphene.Boolean(required=True)


class PromotionUpdateVisible(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    promotion = graphene.Field(PromotionNode)

    class Arguments:
        input = PromotionVisibleInput(required=True)

    def mutate(root, info, input):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                promotion = Promotion.objects.filter(id=input.promotion_id).first()
                promotion.visible = input.visible
                promotion.save()
                return PromotionUpdateVisible(status=True, promotion=promotion)
            else:
                error = Error(code="MASTER_DATA_14", message=MasterDataError.MASTER_DATA_14)
                return PromotionUpdateVisible(status=False, error=error)
        except:
            raise Exception('you must be logged in')


class CountryUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = CountryInput(required=True)

    status = graphene.Boolean()
    country = graphene.Field(CountryNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input=None):
        country = Country.objects.get(pk=id)
        if country:
            country.item_code = input.item_code
            country.status = input.status
            country.name = input.names[0].name
            country.save()
            for name in input.names:
                country.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                country.save()
            return CountryUpdate(status=True, country=country)
        return CountryUpdate(status=False, country=None)


class CountryStateUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = CountryStateInput(required=True)

    status = graphene.Boolean()
    country_state = graphene.Field(CountryStateNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input=None):
        try:
            user = GetToken.getToken(info).user
            if user.isAdmin():
                if not Country.objects.filter(pk=input.country, status=True).exists():
                    error = Error(code="MASTER_DATA_16", message=MasterDataError.MASTER_DATA_16)
                    return CountryStateUpdate(status=False, error=error)

                if CountryState.objects.filter(pk=id).exists():
                    query = Q()
                    query.add(~Q(id=id), Q.AND)
                    query.add(Q(state_code=input.item_code, country_id=input.country), Q.AND)
                    if CountryState.objects.filter(query).exists():
                        error = Error(code="MASTER_DATA_13", message=MasterDataError.MASTER_DATA_13)
                        return CountryStateUpdate(status=False, error=error)

                    country_state = CountryState.objects.get(pk=id)
                    country_state.state_code = input.item_code
                    country_state.status = input.status
                    country_state.name = input.names[0].name
                    country_state.country_id = input.country
                    country_state.save()
                    for name in input.names:
                        country_state.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                        country_state.save()
                    return CountryStateUpdate(status=True, country_state=country_state)

                error = Error(code="MASTER_DATA_17", message=MasterDataError.MASTER_DATA_17)
                return CountryStateUpdate(status=False, error=error)
            else:
                error = Error(code="MASTER_DATA_14", message=MasterDataError.MASTER_DATA_14)
                return CountryStateUpdate(status=False, error=error)
        except:
            raise Exception('you must be logged in')


class CountryStatusInput(graphene.InputObjectType):
    country_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class CountryUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(CountryStatusInput, required=True)

    def mutate(root, info, list_status):
        for country_status in list_status:
            country = Country.objects.get(id=country_status.country_id)
            country.status = country_status.status
            country.save()
        return CountryUpdateStatus(status=True)


class CountryStateStatusInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class CountryStateUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(CountryStateStatusInput, required=True)

    def mutate(root, info, list_status):
        try:
            user = GetToken.getToken(info).user
            if user.isAdmin():
                for country_state_status in list_status:
                    if CountryState.objects.filter(id=country_state_status.id).exists():
                        country_state = CountryState.objects.get(id=country_state_status.id)
                        country_state.status = country_state_status.status
                        country_state.save()
                    else:
                        error = Error(code="MASTER_DATA_17", message=MasterDataError.MASTER_DATA_17)
                        return CountryStateUpdateStatus(status=False, error=error)
                return CountryStateUpdateStatus(status=True)
            else:
                error = Error(code="MASTER_DATA_14", message=MasterDataError.MASTER_DATA_14)
                return CountryStateUpdateStatus(status=False, error=error)
        except:
            raise Exception('you must be logged in')


class CurrencyUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = CurrencyInput(required=True)

    status = graphene.Boolean()
    currency = graphene.Field(CurrencyNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        currency = Currency.objects.get(pk=id)
        if currency:
            currency.item_code = input.item_code
            currency.status = input.status
            currency.name = input.names[0].name
            currency.save()
            for name in input.names:
                currency.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                currency.save()
            return CurrencyUpdate(status=True, currency=currency)
        return CurrencyUpdate(status=False, currency=None)


class CurrencyStatusInput(graphene.InputObjectType):
    currency_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class CurrencyUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(CurrencyStatusInput, required=True)

    def mutate(root, info, list_status):
        for currency_status in list_status:
            currency = Currency.objects.get(id=currency_status.currency_id)
            currency.status = currency_status.status
            currency.save()
        return CurrencyUpdateStatus(status=True)


class ContractTypeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ContractTypeInput(required=True)

    status = graphene.Boolean()
    contract_type = graphene.Field(ContractTypeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        contract_type = ContractType.objects.get(pk=id)
        if contract_type:
            contract_type.status = input.status
            contract_type.name = input.names[0].name
            contract_type.save()
            for name in input.names:
                contract_type.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                contract_type.save()
            return ContractTypeUpdate(status=True, contract_type=contract_type)
        return ContractTypeUpdate(status=False, contract_type=None)


class ContractTypeStatusInput(graphene.InputObjectType):
    contract_type_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class ContractTypeUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(ContractTypeStatusInput, required=True)

    def mutate(root, info, list_status):
        for contract_type_status in list_status:
            contract_type = ContractType.objects.get(id=contract_type_status.contract_type_id)
            contract_type.status = contract_type_status.status
            contract_type.save()
        return ContractTypeUpdateStatus(status=True)


class PaymentTermUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = PaymentTermInput(required=True)

    status = graphene.Boolean()
    payment_term = graphene.Field(PaymentTermNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        payment_term = PaymentTerm.objects.get(pk=id)
        if payment_term:
            payment_term.status = input.status
            for name in input.names:
                payment_term.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                if (name.language_code == 'en'):
                    payment_term.name = name.name
            payment_term.save()
            return PaymentTermUpdate(status=True, payment_term=payment_term)
        return PaymentTermUpdate(status=False, payment_term=None)


class PaymentTermStatusInput(graphene.InputObjectType):
    payment_term_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class PaymentTermUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(PaymentTermStatusInput, required=True)

    def mutate(root, info, list_status):
        for payment_term_status in list_status:
            payment_term = PaymentTerm.objects.get(id=payment_term_status.payment_term_id)
            payment_term.status = payment_term_status.status
            payment_term.save()
        return PaymentTermUpdateStatus(status=True)


class DeliveryTermUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = DeliveryTermInput(required=True)

    status = graphene.Boolean()
    delivery_term = graphene.Field(DeliveryTermNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        delivery_term = DeliveryTerm.objects.get(pk=id)
        if delivery_term:
            delivery_term.status = input.status
            delivery_term.name = input.names[0].name
            delivery_term.save()
            for name in input.names:
                delivery_term.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                delivery_term.save()
            return DeliveryTermUpdate(status=True, delivery_term=delivery_term)
        return DeliveryTermUpdate(status=False, delivery_term=None)


class DeliveryTermStatusInput(graphene.InputObjectType):
    delivery_term_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class DeliveryTermUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(DeliveryTermStatusInput, required=True)

    def mutate(root, info, list_status):
        for delivery_term_status in list_status:
            delivery_term = DeliveryTerm.objects.get(id=delivery_term_status.delivery_term_id)
            delivery_term.status = delivery_term_status.status
            delivery_term.save()
        return DeliveryTermUpdateStatus(status=True)


class UnitofMeasureUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = UnitofMeasureInput(required=True)

    status = graphene.Boolean()
    unit_of_measure = graphene.Field(UnitofMeasureNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        unit_of_measure = UnitofMeasure.objects.get(pk=id)
        if unit_of_measure:
            unit_of_measure.item_code = input.item_code
            unit_of_measure.status = input.status
            for name in input.names:
                unit_of_measure.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                if name.language_code == "en":
                    unit_of_measure.name = name.name

            unit_of_measure.save()
            return UnitofMeasureUpdate(status=True, unit_of_measure=unit_of_measure)
        return UnitofMeasureUpdate(status=False, unit_of_measure=None)


class UnitofMeasureStatusInput(graphene.InputObjectType):
    unit_of_measure_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class UnitofMeasureUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(UnitofMeasureStatusInput, required=True)

    def mutate(root, info, list_status):
        for unit_of_measure_status in list_status:
            unit_of_measure = UnitofMeasure.objects.get(id=unit_of_measure_status.unit_of_measure_id)
            unit_of_measure.status = unit_of_measure_status.status
            unit_of_measure.save()
        return UnitofMeasureUpdateStatus(status=True)


class EmailTemplatesUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = EmailTemplatesInput(required=True)

    status = graphene.Boolean()
    email_templates = graphene.Field(EmailTemplatesNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        email_templates = EmailTemplates.objects.get(pk=id)
        if email_templates:
            email_templates.item_code = input.item_code
            email_templates.variables = input.variables
            email_templates.status = input.status
            email_templates.updated = timezone.now()
            email_templates.title = input.email_templates_languages[0].title
            email_templates.content = input.email_templates_languages[0].content
            email_templates.save()
            for email_templates_language in input.email_templates_languages:
                email_templates.translations.update_or_create(
                    language_code=email_templates_language.language_code,
                    defaults={"title": email_templates_language.title, "content": email_templates_language.content},
                )
                email_templates.save()

            return EmailTemplatesUpdate(status=True, email_templates=email_templates)
        return EmailTemplatesUpdate(status=False, email_templates=None)


class EmailTemplatesStatusInput(graphene.InputObjectType):
    email_templates_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class EmailTemplatesUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(EmailTemplatesStatusInput, required=True)

    def mutate(root, info, list_status):
        for email_templates_status in list_status:
            email_templates = EmailTemplates.objects.get(id=email_templates_status.email_templates_id)
            email_templates.status = email_templates_status.status
            email_templates.save()
        return EmailTemplatesUpdateStatus(status=True)


class NumberofEmployeeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = NumberofEmployeeInput(required=True)

    status = graphene.Boolean()
    number_of_employee = graphene.Field(NumberofEmployeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        number_of_employee = NumberofEmployee.objects.get(pk=id)
        if number_of_employee:
            number_of_employee.status = input.status
            number_of_employee.name = input.names[0].name
            number_of_employee.save()
            for name in input.names:
                number_of_employee.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                number_of_employee.save()
            return NumberofEmployeeUpdate(status=True, number_of_employee=number_of_employee)
        return NumberofEmployeeUpdate(status=False, number_of_employee=None)


class NumberofEmployeeStatusInput(graphene.InputObjectType):
    number_of_employee_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class NumberofEmployeeUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(NumberofEmployeeStatusInput, required=True)

    def mutate(root, info, list_status):
        for number_of_employee_status in list_status:
            number_of_employee = NumberofEmployee.objects.get(id=number_of_employee_status.number_of_employee_id)
            number_of_employee.status = number_of_employee_status.status
            number_of_employee.save()
        return NumberofEmployeeUpdateStatus(status=True)


class GenderUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = GenderInput(required=True)

    status = graphene.Boolean()
    gender = graphene.Field(GenderNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        gender = Gender.objects.get(pk=id)
        if gender:
            gender.status = input.status
            gender.name = input.names[0].name
            gender.save()
            for name in input.names:
                gender.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                gender.save()
            return GenderUpdate(status=True, gender=gender)
        return GenderUpdate(status=False, gender=None)


class GenderStatusInput(graphene.InputObjectType):
    gender_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class GenderUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(GenderStatusInput, required=True)

    def mutate(root, info, list_status):
        for gender_status in list_status:
            gender = Gender.objects.get(id=gender_status.gender_id)
            gender.status = gender_status.status
            gender.save()
        return GenderUpdateStatus(status=True)


class TechnicalWeightingUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = TechnicalWeightingInput(required=True)

    status = graphene.Boolean()
    technical_weighting = graphene.Field(TechnicalWeightingNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        technical_weighting = TechnicalWeighting.objects.get(pk=id)
        if technical_weighting:
            technical_weighting.status = input.status
            technical_weighting.name = input.names[0].name
            technical_weighting.save()
            for name in input.names:
                technical_weighting.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                technical_weighting.save()
            return TechnicalWeightingUpdate(status=True, technical_weighting=technical_weighting)
        return TechnicalWeightingUpdate(status=False, technical_weighting=None)


class TechnicalWeightingStatusInput(graphene.InputObjectType):
    technical_weighting_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class TechnicalWeightingUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(TechnicalWeightingStatusInput, required=True)

    def mutate(root, info, list_status):
        for technical_weighting_status in list_status:
            technical_weighting = TechnicalWeighting.objects.get(id=technical_weighting_status.technical_weighting_id)
            technical_weighting.status = technical_weighting_status.status
            technical_weighting.save()
        return TechnicalWeightingUpdateStatus(status=True)


class AuctionTypeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = AuctionTypeInput(required=True)

    status = graphene.Boolean()
    auction_type = graphene.Field(AuctionTypeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        auction_type = AuctionType.objects.get(pk=id)
        if auction_type:
            auction_type.status = input.status
            auction_type.name = input.names[0].name
            auction_type.save()
            for name in input.names:
                auction_type.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                auction_type.save()
            return AuctionTypeUpdate(status=True, auction_type=auction_type)
        return AuctionTypeUpdate(status=False, auction_type=None)


class AuctionTypeStatusInput(graphene.InputObjectType):
    auction_type_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class AuctionTypeUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(AuctionTypeStatusInput, required=True)

    def mutate(root, info, list_status):
        for auction_type_status in list_status:
            auction_type = AuctionType.objects.get(id=auction_type_status.auction_type_id)
            auction_type.status = auction_type_status.status
            auction_type.save()
        return AuctionTypeUpdateStatus(status=True)


class PositionUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = PositionInput(required=True)

    status = graphene.Boolean()
    position = graphene.Field(PositionNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        position = Position.objects.get(pk=id)
        if position:
            position.name = input.names[0].name
            position.status = input.status
            position.save()
            for name in input.names:
                position.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                position.save()

            return PositionUpdate(status=True, position=position)
        return PositionUpdate(status=False, position=None)


class PositionStatusInput(graphene.InputObjectType):
    position_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class PositionUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(PositionStatusInput, required=True)

    def mutate(root, info, list_status):
        for position_status in list_status:
            position = Position.objects.get(id=position_status.position_id)
            position.status = position_status.status
            position.save()
        return PositionUpdateStatus(status=True)


class LevelUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = LevelInput(required=True)

    status = graphene.Boolean()
    level = graphene.Field(LevelNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        level = Level.objects.get(pk=id)
        if level:
            level.status = input.status
            level.name = input.names[0].name
            level.save()
            for name in input.names:
                level.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                level.save()
            return LevelUpdate(status=True, level=level)
        return LevelUpdate(status=False, level=None)


class LevelStatusInput(graphene.InputObjectType):
    level_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class LevelUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(LevelStatusInput, required=True)

    def mutate(root, info, list_status):
        for level_status in list_status:
            level = Level.objects.get(id=level_status.level_id)
            level.status = level_status.status
            level.save()
        return LevelUpdateStatus(status=True)


class FamilyCodeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = FamilyCodeInput(required=True)

    status = graphene.Boolean()
    family_code = graphene.Field(FamilyCodeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        family_code = FamilyCode.objects.get(pk=id)
        if len(input.item_code) >= 3:
            error = Error(code="MASTER_DATA_01", message=MasterDataError.MASTER_DATA_01)
            return FamilyCodeUpdate(status=False, error=error)
        if family_code:
            family_code.item_code = input.item_code
            family_code.status = input.status
            if len(family_code.item_code) < 2:
                family_code.item_code = '0' + family_code.item_code
            for name in input.names:
                family_code.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                if name.language_code == 'en':
                    family_code.name = name.name
            family_code.save()
            return FamilyCodeUpdate(status=True, family_code=family_code)
        return FamilyCodeUpdate(status=False, family_code=None)


class FamilyCodeStatusInput(graphene.InputObjectType):
    family_code_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class FamilyCodeUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(FamilyCodeStatusInput, required=True)

    def mutate(root, info, list_status):
        for family_code_status in list_status:
            family_code = FamilyCode.objects.get(id=family_code_status.family_code_id)
            family_code.status = family_code_status.status
            family_code.save()
        return FamilyCodeUpdateStatus(status=True)


class ClusterCodeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ClusterCodeInput(required=True)

    status = graphene.Boolean()
    cluster_code = graphene.Field(ClusterCodeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        cluster_code = ClusterCode.objects.get(pk=id)
        if len(input.item_code) >= 4:
            error = Error(code="MASTER_DATA_07", message=MasterDataError.MASTER_DATA_07)
            return ClusterCodeUpdate(status=False, error=error)
        if cluster_code:
            cluster_code.item_code = input.item_code
            cluster_code.status = input.status
            if len(cluster_code.item_code) < 2:
                cluster_code.item_code = '0' + cluster_code.item_code
            for name in input.names:
                cluster_code.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                if name.language_code == 'en':
                    cluster_code.name = name.name
            cluster_code.save()
            return ClusterCodeUpdate(status=True, cluster_code=cluster_code)
        return ClusterCodeUpdate(status=False, cluster_code=None)


class ClusterCodeStatusInput(graphene.InputObjectType):
    cluster_code_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class ClusterCodeUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(ClusterCodeStatusInput, required=True)

    def mutate(root, info, list_status):
        for cluster_code_status in list_status:
            cluster_code = ClusterCode.objects.get(id=cluster_code_status.cluster_code_id)
            cluster_code.status = cluster_code_status.status
            cluster_code.save()
        return ClusterCodeUpdateStatus(status=True)


class SubClusterCodeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = SubClusterCodeInput(required=True)

    status = graphene.Boolean()
    sub_cluster_code = graphene.Field(SubClusterCodeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        sub_cluster_code = SubClusterCode.objects.get(pk=id)
        if len(input.item_code) >= 5:
            error = Error(code="MASTER_DATA_08", message=MasterDataError.MASTER_DATA_08)
            return SubClusterCodeUpdate(status=False, error=error)
        if sub_cluster_code:
            sub_cluster_code.item_code = input.item_code
            sub_cluster_code.status = input.status
            if len(sub_cluster_code.item_code) < 2:
                sub_cluster_code.item_code = '0' + sub_cluster_code.item_code
            for name in input.names:
                sub_cluster_code.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                if name.language_code == 'en':
                    sub_cluster_code.name = name.name
            sub_cluster_code.save()
            return SubClusterCodeUpdate(status=True, sub_cluster_code=sub_cluster_code)
        return SubClusterCodeUpdate(status=False, sub_cluster_code=None)


class SubClusterCodeStatusInput(graphene.InputObjectType):
    sub_cluster_code_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class SubClusterCodeUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(SubClusterCodeStatusInput, required=True)

    def mutate(root, info, list_status):
        for sub_cluster_code_status in list_status:
            sub_cluster_code = SubClusterCode.objects.get(id=sub_cluster_code_status.sub_cluster_code_id)
            sub_cluster_code.status = sub_cluster_code_status.status
            sub_cluster_code.save()
        return SubClusterCodeUpdateStatus(status=True)


class CategoryUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = CategoryInput(required=True)

    status = graphene.Boolean()
    category = graphene.Field(CategoryNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        category = Category.objects.get(pk=id)
        if len(input.item_code) >= 6:
            error = Error(code="MASTER_DATA_09", message=MasterDataError.MASTER_DATA_09)
            return CategoryUpdate(status=False, error=error)
        if category:
            category.item_code = input.item_code
            category.status = input.status
            if len(category.item_code) < 2:
                category.item_code = '0' + category.item_code
            for name in input.names:
                category.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                if name.language_code == 'en':
                    category.name = name.name
            category.save()
            return CategoryUpdate(status=True, category=category)
        return CategoryUpdate(status=False, category=None)


class CategoryStatusInput(graphene.InputObjectType):
    category_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class CategoryUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(CategoryStatusInput, required=True)

    def mutate(root, info, list_status):
        for category_status in list_status:
            category = Category.objects.get(id=category_status.category_id)
            category.status = category_status.status
            category.save()
        return CategoryUpdateStatus(status=True)


class SupplierListUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = SupplierListInput(required=True)

    status = graphene.Boolean()
    supplier_list = graphene.Field(SupplierListNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        supplier_list = SupplierList.objects.get(pk=id)
        if supplier_list:
            supplier_list.name = input.name
            supplier_list.status = input.status
            supplier_list.save()
            return SupplierListUpdate(status=True, supplier_list=supplier_list)
        return SupplierListUpdate(status=False, supplier_list=None)


class SupplierListStatusInput(graphene.InputObjectType):
    supplier_list_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class SupplierListUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(SupplierListStatusInput, required=True)

    def mutate(root, info, list_status):
        for supplier_list_status in list_status:
            supplier_list = SupplierList.objects.get(id=supplier_list_status.supplier_list_id)
            supplier_list.status = supplier_list_status.status
            supplier_list.save()
        return SupplierListUpdateStatus(status=True)


class EmailListUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = EmailListInput(required=True)

    status = graphene.Boolean()
    email_list = graphene.Field(EmailListNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        email_list = EmailList.objects.get(pk=id)
        if email_list:
            email_list.email = input.email
            email_list.country = input.country
            email_list.status = input.status
            email_list.save()
            return EmailListUpdate(status=True, email_list=email_list)
        return EmailListUpdate(status=False, email_list=None)


class EmailListStatusInput(graphene.InputObjectType):
    email_list_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class EmailListUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(EmailListStatusInput, required=True)

    def mutate(root, info, list_status):
        for email_list_status in list_status:
            email_list = EmailList.objects.get(id=email_list_status.email_list_id)
            email_list_status = email_list_status.status
            email_list.save()
        return EmailListUpdateStatus(status=True)


class ExchangeRateUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ExchangeRateInput(required=True)

    status = graphene.Boolean()
    exchange_rate = graphene.Field(ExchangeRateNode)

    def mutate(root, info, id, input=None):
        status = False
        exchange_rate_instance = ExchangeRate.objects.get(pk=id)
        if exchange_rate_instance:
            status = True
            exchange_rate_instance.unit_of_measures_name = input.unit_of_measures_name
            exchange_rate_instance.item_code = input.item_code
            exchange_rate_instance.exchange_rate = input.exchange_rate
            exchange_rate_instance.status = input.status
            exchange_rate_instance.save()
            return ExchangeRateUpdate(status=status, exchange_rate=exchange_rate_instance)
        return ExchangeRateUpdate(status=status, exchange_rate=None)


class CouponUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = CouponInput(required=True)

    error = graphene.Field(Error)
    status = graphene.Boolean()
    coupon = graphene.Field(CouponNode)

    def mutate(root, info, id, input):
        if input.commission <= 0 or input.commission > 100:
            error = Error(code="MASTER_DATA_10", message=MasterDataError.MASTER_DATA_10)
            return CouponUpdate(status=False, error=error)

        if input.valid_from > input.valid_to:
            error = Error(code="MASTER_DATA_12", message=MasterDataError.MASTER_DATA_12)
            return CouponUpdate(status=False, error=error)

        coupon = Coupon.objects.get(pk=id)
        if coupon:
            coupon.coupon_program = input.coupon_program
            if Coupon.objects.filter(coupon_program=input.coupon_program).exclude(id=coupon.id):
                error = Error(code="MASTER_DATA_11", message=MasterDataError.MASTER_DATA_11)
                return CouponUpdate(status=False, error=error)
            coupon.description = input.description
            coupon.commission = input.commission
            coupon.valid_from = input.valid_from
            coupon.valid_to = input.valid_to
            coupon.note = input.note
            coupon.email = input.email
            coupon.full_name = input.full_name
            coupon.status = input.status
            coupon.save()
            return CouponUpdate(status=True, coupon=coupon)
        return CouponUpdate(status=False, coupon=None)


class CouponStatusInput(graphene.InputObjectType):
    coupon_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class CouponUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(CouponStatusInput, required=True)

    def mutate(root, info, list_status):
        for coupon_status in list_status:
            coupon = Coupon.objects.get(id=coupon_status.coupon_id)
            coupon.status = coupon_status.status
            coupon.save()
        return CouponUpdateStatus(status=True)


class BankUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = BankInput(required=True)

    status = graphene.Boolean()
    bank = graphene.Field(BankNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        bank = Bank.objects.get(pk=id)
        if bank:
            if Bank.objects.filter(item_code=input.item_code).exclude(id=bank.id):
                error = Error(code="MASTER_DATA_13", message=MasterDataError.MASTER_DATA_13)
                return CouponUpdate(status=False, error=error)
            bank.item_code = input.item_code
            bank.name = input.name
            bank.save()

            return BankUpdate(status=True, bank=bank)
        return BankUpdate(status=False, bank=None)


class BankStatusInput(graphene.InputObjectType):
    bank_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class BankUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(BankStatusInput, required=True)

    def mutate(root, info, list_status):
        for bank_status in list_status:
            bank = Bank.objects.get(id=bank_status.bank_id)
            bank.status = bank_status.status
            bank.save()
        return BankUpdateStatus(status=True)

class VoucherUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = VoucherInput(required=True)

    status = graphene.Boolean()
    voucher = graphene.Field(VoucherNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            error = None
            voucher = Voucher.objects.get(pk=id)
            if len(input.voucher_code) != 3:
                error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
                return VoucherUpdate(status=False, error=error)
            if input.discount < 0 or input.discount > 100:
                error = Error(code="MASTER_DATA_00", message='discount is not in range {}-{}'.format(0,100))
                return VoucherUpdate(status=False, error=error)
            if voucher:
                voucher.voucher_code = input.voucher_code
                voucher.status = input.status
                voucher.discount = input.discount
                voucher.label = input.label
                for name in input.names:
                    voucher.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                    if name.language_code == 'en':
                        voucher.name = name.name
                    voucher.save()
                return VoucherUpdate(status=True, voucher=voucher)
        except Exception as err:
            transaction.set_rollback(True)
            return VoucherUpdate(status=False,error=error)

class VoucherStatusInput(graphene.InputObjectType):
    voucher_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)

class VoucherUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(VoucherStatusInput, required=True)

    def mutate(root, info, list_status):
        for voucher_status in list_status:
            voucher = Voucher.objects.get(id=voucher_status.voucher_id)
            voucher.status = voucher_status.status
            voucher.save()
        return VoucherUpdateStatus(status=True)

class BuyerClubVoucherUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = BuyerClubVoucherInput(required=True)

    status = graphene.Boolean()
    buyer_club_voucher = graphene.Field(BuyerClubVoucherNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            error = None
            buyer_club_voucher = BuyerClubVoucher.objects.get(pk=id)
            if len(input.voucher_code) != 3:
                error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
                return BuyerClubVoucherUpdate(status=False, error=error)
            if not (0 <= input.standard <= 100) or not (0 <= input.gold <= 100) or not (0 <= input.platinum <= 100) or not (0 <= input.diamond <= 100):
                error = Error(code="MASTER_DATA_00", message='discount is not in range {}-{}'.format(0,100))
                return BuyerClubVoucherUpdate(status=False, error=error)
            if buyer_club_voucher:
                buyer_club_voucher.voucher_code = input.voucher_code
                buyer_club_voucher.status = input.status
                buyer_club_voucher.discount = input.discount
                buyer_club_voucher.label = input.label
                for description in input.descriptions:
                    buyer_club_voucher.translations.update_or_create(language_code=description.language_code, defaults={"description": description.description})
                    if description.language_code == 'en':
                        buyer_club_voucher.description = description.description
                    buyer_club_voucher.save()
                return BuyerClubVoucherUpdate(status=True, buyer_club_voucher=buyer_club_voucher)
        except Exception as err:
            transaction.set_rollback(True)
            return BuyerClubVoucherUpdate(status=False,error=error)

    
class BuyerClubVoucherStatusInput(graphene.InputObjectType):
    voucher_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class BuyerClubVoucherStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(BuyerClubVoucherStatusInput, required=True)

    def mutate(root, info, list_status):
        for voucher_status in list_status:
            buyer_club_voucher = BuyerClubVoucher.objects.get(id=voucher_status.voucher_id)
            buyer_club_voucher.status = voucher_status.status
            buyer_club_voucher.save()
        return BuyerClubVoucherStatusUpdate(status=True)

class WarrantyTermUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = WarrantyTermInput(required=True)

    status = graphene.Boolean()
    warranty_term = graphene.Field(WarrantyTermNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            error = None
            warranty_term = WarrantyTerm.objects.get(pk=id)

            if len(input.warranty_code) != 3:
                error = Error(code="MASTER_DATA_02", message=MasterDataError.MASTER_DATA_02)
                return WarrantyTermUpdate(status=False, error=error)
            if  warranty_term:
                warranty_term.warranty_code = input.warranty_code
                warranty_term.status = input.status
                for name in input.names:
                    warranty_term.translations.update_or_create(language_code=name.language_code, defaults={"name": name.name})
                    if name.language_code == 'en':
                        warranty_term.name = name.name
                    warranty_term.save()
                return WarrantyTermUpdate(status=True,  warranty_term= warranty_term)
        except Exception as err:
            transaction.set_rollback(True)
            return WarrantyTermUpdate(status=False,error=error)

class WarrantyTermStatusInput(graphene.InputObjectType):
    warranty_term_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class WarrantyTermUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(WarrantyTermStatusInput, required=True)

    def mutate(root, info, list_status):
        for warranty_term_status in list_status:
            warranty_term = WarrantyTerm.objects.get(id= warranty_term_status. warranty_term_id)
            warranty_term.status = warranty_term_status.status
            warranty_term.save()
        return WarrantyTermUpdateStatus(status=True)

class SetProductAdvertisementUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = SetProductAdvertisementInput(required=True)

    status = graphene.Boolean()
    set_product_advertisement = graphene.Field(SetProductAdvertisementNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            error = None
            set_product_advertisement = SetProductAdvertisement.objects.get(pk=id)

            if input.duration < 1 or input.duration > 365:
                error = Error(code="MASTER_DATA_00", message='duration is not in range {}-{}'.format(1,365))
                return SetProductAdvertisementUpdate(status=False, error=error)

            if  set_product_advertisement:
                set_product_advertisement.duration = input.duration
                set_product_advertisement.serviceFee = input.serviceFee
                set_product_advertisement.status = input.status
                for description in input.descriptions:
                    set_product_advertisement.translations.update_or_create(language_code=description.language_code, defaults={"description": description.description})
                    if description.language_code == 'en':
                        set_product_advertisement.description = description.description
                    set_product_advertisement.save()
                return SetProductAdvertisementUpdate(status=True,  set_product_advertisement= set_product_advertisement)
        except Exception as err:
            transaction.set_rollback(True)
            return SetProductAdvertisementUpdate(status=False,error=error)

class SetProductAdvertisementStatusInput(graphene.InputObjectType):
    set_product_advertisement_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class SetProductAdvertisementUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(SetProductAdvertisementStatusInput, required=True)

    def mutate(root, info, list_status):
        for set_product_advertisement_status in list_status:
            set_product_advertisement = SetProductAdvertisement.objects.get(id= set_product_advertisement_status. set_product_advertisement_id)
            set_product_advertisement.status = set_product_advertisement_status.status
            set_product_advertisement.save()
        return SetProductAdvertisementUpdateStatus(status=True)
# --------------------------DELETE-------------------------


class ReasonDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        reason = Reason.objects.get(pk=id)
        reason.delete()
        return ReasonDelete(status=True)


class LanguageDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        language = Language.objects.get(pk=id)
        language.delete()
        return LanguageDelete(status=True)


class ClientFocusDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        client_focus = ClientFocus.objects.get(pk=id)
        client_focus.delete()
        return ClientFocusDelete(status=True)


class IndustryDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        industry = Industry.objects.get(pk=id)
        industry.delete()
        return IndustryDelete(status=True)


class IndustryClusterDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        industry_cluster = IndustryCluster.objects.get(pk=id)
        industry_cluster.delete()
        return IndustryClusterDelete(status=True)


class IndustrySectorsDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        industry_sectors = IndustrySectors.objects.get(pk=id)
        industry_sectors.delete()
        return IndustrySectorsDelete(status=True)


class IndustrySubSectorsDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        industry_sub_sector = IndustrySubSectors.objects.get(pk=id)
        industry_sub_sector.delete()
        return IndustrySubSectorsDelete(status=True)


class PromotionDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        promotion = Promotion.objects.get(pk=id)
        promotion.delete()
        return PromotionDelete(status=True)


class CountryDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        country = Country.objects.get(pk=id)
        country.delete()
        return CountryDelete(status=True)


class CurrencyDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        currency = Currency.objects.get(pk=id)
        currency.delete()
        return CurrencyDelete(status=True)


class ContractTypeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        contract_type = ContractType.objects.get(pk=id)
        contract_type.delete()
        return ContractTypeDelete(status=True)


class PaymentTermDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        payment_term = PaymentTerm.objects.get(pk=id)
        payment_term.delete()
        return PaymentTermDelete(status=True)


class DeliveryTermDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        delivery_term = DeliveryTerm.objects.get(pk=id)
        delivery_term.delete()
        return DeliveryTermDelete(status=True)


class UnitofMeasureDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        unit_of_measure = UnitofMeasure.objects.get(pk=id)
        unit_of_measure.delete()
        return UnitofMeasureDelete(status=True)


class EmailTemplatesDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        email_templates = EmailTemplates.objects.get(pk=id)
        email_templates.delete()
        return EmailTemplatesDelete(status=True)


class NumberofEmployeeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        number_of_employee = NumberofEmployee.objects.get(pk=id)
        number_of_employee.delete()
        return NumberofEmployeeDelete(status=True)


class GenderDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        gender = Gender.objects.get(pk=id)
        gender.delete()
        return GenderDelete(status=True)


class TechnicalWeightingDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        technical_weighting = TechnicalWeighting.objects.get(pk=id)
        technical_weighting.delete()
        return TechnicalWeightingDelete(status=True)


class AuctionTypeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        auction_type = AuctionType.objects.get(pk=id)
        auction_type.delete()
        return AuctionTypeDelete(status=True)


class PositionDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        position = Position.objects.get(pk=id)
        position.delete()
        return PositionDelete(status=True)


class LevelDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        level = Level.objects.get(pk=id)
        level.delete()
        return LevelDelete(status=True)


class FamilyCodeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        family_code = FamilyCode.objects.get(pk=id)
        family_code.delete()
        return FamilyCodeDelete(status=True)


class ClusterCodeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        cluster_code = ClusterCode.objects.get(pk=id)
        cluster_code.delete()
        return ClusterCodeDelete(status=True)


class SubClusterCodeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        sub_cluster_code = SubClusterCode.objects.get(pk=id)
        sub_cluster_code.delete()
        return SubClusterCodeDelete(status=True)


class CategoryDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        category = Category.objects.get(pk=id)
        category.delete()
        return CategoryDelete(status=True)


class SupplierListDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        supplier_list = SupplierList.objects.get(pk=id)
        supplier_list.delete()
        return SupplierListDelete(status=True)


class EmailListDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        email_list = EmailList.objects.get(pk=id)
        email_list.delete()
        return EmailListDelete(status=True)


class ExchangeRateDelete(graphene.Mutation):
    status = graphene.Boolean()

    def mutate(root, info, id, **kwargs):
        change_rate_instance = ExchangeRate.objects.get(pk=id).delete()
        return ExchangeRateDelete(status=True)


class CouponDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        coupon = Coupon.objects.get(pk=id)
        coupon.delete()
        return CouponDelete(status=True)


class BankDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        bank = Bank.objects.get(pk=id).delete()
        return BankDelete(status=True)

class VoucherDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        try:
            voucher = Voucher.objects.get(pk=id)
            voucher.delete()
            return VoucherDelete(status=True)
        except Exception as err:
            return VoucherDelete(status=False, error=err)
            
class BuyerClubVoucherDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        try:
            voucher = BuyerClubVoucher.objects.get(pk=id)
            voucher.delete()
            return BuyerClubVoucherDelete(status=True)
        except Exception as err:
            return BuyerClubVoucherDelete(status=False, error=err)

class WarrantyTermDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        warrantyTerm = WarrantyTerm.objects.get(pk=id)
        warrantyTerm.delete()
        return WarrantyTermDelete(status=True)

class SetProductAdvertisementDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        set_product_advertisement = SetProductAdvertisement.objects.get(pk=id)
        set_product_advertisement.delete()
        return SetProductAdvertisementDelete(status=True)

# ------------------------translation------------------------


class CountryTranslationInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language_code = graphene.String(default_value="en")


class CountryTranslationUpdate(graphene.Mutation):
    class Arguments:
        country_id = graphene.ID(required=True)
        input = CountryTranslationInput(required=True)

    country = graphene.Field(CountryNode)
    error = graphene.Field(Error)
    status = graphene.Boolean()

    def mutate(root, info, input, country_id):
        country = Country.objects.get(id=country_id)
        country.translations.update_or_create(language_code=input.language_code, defaults=input)
        return CountryTranslationUpdate(status=True, country=country)

# ----------------------------------------------QUERY---------------------------------------------------


class Query(object):
    # ------------------------------------------Search Industry---------------------------------------

    search_industry = relay.ConnectionField(IndustryConnection, name=graphene.String())

    def resolve_search_industry(self, info, **kwargs):
        language_code = translation.get_language()
        industry = Industry.objects.filter(translations__name__icontains=kwargs.get('name'), translations__language_code=language_code)
        industry_cluster = IndustryCluster.objects.filter(translations__name__icontains=kwargs.get('name'), translations__language_code=language_code)
        industry_sectors = IndustrySectors.objects.filter(translations__name__icontains=kwargs.get('name'), translations__language_code=language_code)
        industry_sub_sectors = IndustrySubSectors.objects.filter(
            translations__name__icontains=kwargs.get('name'), translations__language_code=language_code
        )

        results = [*industry, *industry_cluster, *industry_sectors, *industry_sub_sectors]
        return results

    # ----------------------------------Search CCC----------------------------------------------

    search_ccc = relay.ConnectionField(CCCConnection, name=graphene.String())

    def resolve_search_ccc(self, info, **kwargs):
        language_code = translation.get_language()
        family_code = FamilyCode.objects.filter(translations__name__icontains=kwargs.get('name'), translations__language_code=language_code)
        cluster_code = ClusterCode.objects.filter(translations__name__icontains=kwargs.get('name'), translations__language_code=language_code)
        sub_cluster_code = SubClusterCode.objects.filter(translations__name__icontains=kwargs.get('name'), translations__language_code=language_code)
        category = Category.objects.filter(translations__name__icontains=kwargs.get('name'), translations__language_code=language_code)
        results = [*family_code, *cluster_code, *sub_cluster_code, *category]
        return results

    family_code = CustomNode.Field(FamilyCodeNode)
    family_codes = CustomizeFilterConnectionField(FamilyCodeNode)

    cluster_code = CustomNode.Field(ClusterCodeNode)
    cluster_codes = CustomizeFilterConnectionField(ClusterCodeNode)

    sub_cluster_code = CustomNode.Field(SubClusterCodeNode)
    sub_cluster_codes = CustomizeFilterConnectionField(SubClusterCodeNode)

    category = CustomNode.Field(CategoryNode)
    categories = CustomizeFilterConnectionField(CategoryNode)

    sponsor = CustomNode.Field(SponsorNode)
    sponsors = CustomizeFilterConnectionField(SponsorNode)

    reason = CustomNode.Field(ReasonNode)
    reasons = CustomizeFilterConnectionField(ReasonNode)

    language = CustomNode.Field(LanguageNode)
    languages = CustomizeFilterConnectionField(LanguageNode)

    industry = CustomNode.Field(IndustryNode)
    industries = CustomizeFilterConnectionField(IndustryNode)

    industry_cluster = CustomNode.Field(IndustryClusterNode)
    industry_clusters = CustomizeFilterConnectionField(IndustryClusterNode)

    industry_sector = CustomNode.Field(IndustrySectorsNode)
    industry_sectors = CustomizeFilterConnectionField(IndustrySectorsNode)

    industry_sub_sector = CustomNode.Field(IndustrySubSectorsNode)
    industry_sub_sectors = CustomizeFilterConnectionField(IndustrySubSectorsNode)

    client_focus = CustomNode.Field(ClientFocusNode)
    client_focuses = CustomizeFilterConnectionField(ClientFocusNode)

    currency = CustomNode.Field(CurrencyNode)
    currencies = CustomizeFilterConnectionField(CurrencyNode)

    number_of_employee = CustomNode.Field(NumberofEmployeeNode)
    number_of_employees = CustomizeFilterConnectionField(NumberofEmployeeNode)

    level = CustomNode.Field(LevelNode)
    levels = CustomizeFilterConnectionField(LevelNode)

    country = CustomNode.Field(CountryNode)
    countries = CustomizeFilterConnectionField(CountryNode)

    country_state = CustomNode.Field(CountryStateNode)
    country_states = CustomizeFilterConnectionField(CountryStateNode)

    promotion = CustomNode.Field(PromotionNode)
    promotions = CustomizeFilterConnectionField(PromotionNode)
    promotion_advertisement = graphene.Field(PromotionNode, promotion_code=graphene.String(required=True))

    promotion_history = CustomNode.Field(PromotionUserUsedNode)
    promotion_histories = CustomizeFilterConnectionField(PromotionUserUsedNode)

    contract_type = CustomNode.Field(ContractTypeNode)
    contract_types = CustomizeFilterConnectionField(ContractTypeNode)

    payment_term = CustomNode.Field(PaymentTermNode)
    payment_terms = CustomizeFilterConnectionField(PaymentTermNode)

    delivery_term = CustomNode.Field(DeliveryTermNode)
    delivery_terms = CustomizeFilterConnectionField(DeliveryTermNode)

    unit_of_measure = CustomNode.Field(UnitofMeasureNode)
    unit_of_measures = CustomizeFilterConnectionField(UnitofMeasureNode)

    email_template = CustomNode.Field(EmailTemplatesNode)
    email_templates = CustomizeFilterConnectionField(EmailTemplatesNode)

    gender = CustomNode.Field(GenderNode)
    genders = CustomizeFilterConnectionField(GenderNode)

    technical_weighting = CustomNode.Field(TechnicalWeightingNode)
    technical_weightings = CustomizeFilterConnectionField(TechnicalWeightingNode)

    auction_type = CustomNode.Field(AuctionTypeNode)
    auction_types = CustomizeFilterConnectionField(AuctionTypeNode)

    position = CustomNode.Field(PositionNode)
    positions = CustomizeFilterConnectionField(PositionNode)

    supplier_list = CustomNode.Field(SupplierListNode)
    supplier_lists = CustomizeFilterConnectionField(SupplierListNode)

    exchange_rate = CustomNode.Field(ExchangeRateNode)
    exchange_rates = CustomizeFilterConnectionField(ExchangeRateNode)

    coupon = CustomNode.Field(CouponNode)
    coupons = CustomizeFilterConnectionField(CouponNode)

    bank = CustomNode.Field(BankNode)
    banks = CustomizeFilterConnectionField(BankNode)

    voucher = CustomNode.Field(VoucherNode)
    vouchers = CustomizeFilterConnectionField(VoucherNode)

    buyerClubVoucher = CustomNode.Field(BuyerClubVoucherNode)
    buyerClubVouchers = CustomizeFilterConnectionField(BuyerClubVoucherNode)

    warranty_term = CustomNode.Field(WarrantyTermNode)
    warranty_terms = CustomizeFilterConnectionField(WarrantyTermNode)

    set_product_advertisement = CustomNode.Field(SetProductAdvertisementNode)
    set_product_advertisements = CustomizeFilterConnectionField(SetProductAdvertisementNode)

    def resolve_all_reason(self, info, **kwargs):
        return Reason.objects.all()

    def resolve_all_language(self, info, **kwargs):
        return Language.objects.all()

    def resolve_all_promotion(self, info, **kwargs):
        return Promotion.objects.all()

    promotion_results = relay.ConnectionField(PromotionConectionResults, promotion_code=graphene.String(required=True), for_supplier_scope=graphene.String())

    def resolve_promotion_results(root, info, promotion_code, for_supplier_scope=None):
        result = []
        user = GetToken.getToken(info).user
        promotion_instance = None
        if user.isAdmin():
            promotion_instance = Promotion.objects.filter(
                name=promotion_code,
                status=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            ).first()
        elif user.isBuyer():
            promotion_instance = Promotion.objects.filter(
                name=promotion_code,
                status=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now(),
                apply_scope=PromotionApplyScope.FOR_BUYER
            ).first()
        elif user.isSupplier():
            if for_supplier_scope:
                if for_supplier_scope == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES:
                    promotion_instance = Promotion.objects.filter(
                        name=promotion_code,
                        status=True,
                        valid_from__lte=timezone.now(),
                        valid_to__gte=timezone.now(),
                        apply_scope__in=[PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES, PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE]
                    ).first()
                elif for_supplier_scope == PromotionApplyScope.FOR_SUPPLIER_SICP:
                    promotion_instance = Promotion.objects.filter(
                        name=promotion_code,
                        status=True,
                        valid_from__lte=timezone.now(),
                        valid_to__gte=timezone.now(),
                        apply_scope__in=[PromotionApplyScope.FOR_SUPPLIER_SICP, PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE]
                    ).first()
            else:
                promotion_instance = None
        result.append(promotion_instance)
        return result

    def resolve_promotion_advertisement(self, info, promotion_code):
        GetToken.getToken(info)
        return Promotion.objects.filter(
            name=promotion_code,
            status=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
            apply_for_advertisement=True
        ).first()

# --------------------------MUTATION-----------------------------


class Mutation(graphene.ObjectType):
    # ----------------------Create---------------------------

    reason_create = ReasonCreate.Field()
    language_create = LanguageCreate.Field()
    promotion_create = PromotionCreate.Field()
    country_create = CountryCreate.Field()
    country_state_create = CountryStateCreate.Field()
    currency_create = CurrencyCreate.Field()
    contract_type_create = ContractTypeCreate.Field()
    payment_term_create = PaymentTermCreate.Field()
    delivery_term_create = DeliveryTermCreate.Field()
    unit_of_measure_create = UnitofMeasureCreate.Field()
    email_templates_create = EmailTemplatesCreate.Field()
    number_of_employee_create = NumberofEmployeeCreate.Field()
    gender_create = GenderCreate.Field()
    technical_weighting_create = TechnicalWeightingCreate.Field()
    auction_type_create = AuctionTypeCreate.Field()
    position_create = PositionCreate.Field()
    level_create = LevelCreate.Field()
    client_focus_create = ClientFocusCreate.Field()
    industry_create = IndustryCreate.Field()
    industry_cluster_create = IndustryClusterCreate.Field()
    industry_sectors_create = IndustrySectorsCreate.Field()
    industry_sub_sectors_create = IndustrySubSectorsCreate.Field()
    family_code_create = FamilyCodeCreate.Field()
    cluster_code_create = ClusterCodeCreate.Field()
    sub_cluster_code_create = SubClusterCodeCreate.Field()
    category_create = CategoryCreate.Field()
    supplier_list_create = SupplierListCreate.Field()
    email_list_create = EmailListCreate.Field()
    exchange_rate_create = ExchangeRateCreate.Field()
    coupon_create = CouponCreate.Field()
    bank_create = BankCreate.Field()
    voucher_create = VoucherCreate.Field()
    buyer_club_voucher_create = BuyerClubVoucherCreate.Field()
    warranty_term_create = WarrantyTermCreate.Field()
    set_product_advertisement_create = SetProductAdvertisementCreate.Field()

    # ------------------------Update--------------------------

    reason_update = ReasonUpdate.Field()
    reason_update_status = ReasonUpdateStatus.Field()
    language_update = LanguageUpdate.Field()
    language_update_status = LanguageUpdateStatus.Field()
    promotion_update = PromotionUpdate.Field()
    promotion_update_status = PromotionUpdateStatus.Field()
    country_update = CountryUpdate.Field()
    country_update_status = CountryUpdateStatus.Field()
    country_state_update = CountryStateUpdate.Field()
    country_state_update_status = CountryStateUpdateStatus.Field()
    currency_update = CurrencyUpdate.Field()
    currency_update_status = CurrencyUpdateStatus.Field()
    contract_type_update = ContractTypeUpdate.Field()
    contract_type_update_status = ContractTypeUpdateStatus.Field()
    payment_term_update = PaymentTermUpdate.Field()
    payment_term_update_status = PaymentTermUpdateStatus.Field()
    delivery_term_update = DeliveryTermUpdate.Field()
    delivery_term_update_status = DeliveryTermUpdateStatus.Field()
    unit_of_measure_update = UnitofMeasureUpdate.Field()
    unit_of_measure_update_status = UnitofMeasureUpdateStatus.Field()
    email_templates_update = EmailTemplatesUpdate.Field()
    email_templates_update_status = EmailTemplatesUpdateStatus.Field()
    number_of_employee_update = NumberofEmployeeUpdate.Field()
    number_of_employee_update_status = NumberofEmployeeUpdateStatus.Field()
    gender_update = GenderUpdate.Field()
    gender_update_status = GenderUpdateStatus.Field()
    technical_weighting_update = TechnicalWeightingUpdate.Field()
    technical_weighting_update_status = TechnicalWeightingUpdateStatus.Field()
    auction_type_update = AuctionTypeUpdate.Field()
    auction_type_update_status = AuctionTypeUpdateStatus.Field()
    position_update = PositionUpdate.Field()
    position_update_status = PositionUpdateStatus.Field()
    level_update = LevelUpdate.Field()
    level_update_status = LevelUpdateStatus.Field()
    industry_update = IndustryUpdate.Field()
    industry_update_status = IndustryUpdateStatus.Field()
    industry_cluster_update = IndustryClusterUpdate.Field()
    industry_cluster_update_status = IndustryClusterUpdateStatus.Field()
    industry_sectors_update = IndustrySectorsUpdate.Field()
    industry_sectors_update_status = IndustrySectorsUpdateStatus.Field()
    industry_sub_sectors_update = IndustrySubSectorsUpdate.Field()
    industry_sub_sectors_update_status = IndustrySubSectorsUpdateStatus.Field()
    client_focus_update = ClientFocusUpdate.Field()
    client_focus_update_status = ClientFocusUpdateStatus.Field()
    family_code_update = FamilyCodeUpdate.Field()
    family_code_update_status = FamilyCodeUpdateStatus.Field()
    cluster_code_update = ClusterCodeUpdate.Field()
    cluster_code_update_status = ClusterCodeUpdateStatus.Field()
    sub_cluster_code_update = SubClusterCodeUpdate.Field()
    sub_cluster_code_update_status = SubClusterCodeUpdateStatus.Field()
    category_update = CategoryUpdate.Field()
    category_update_status = CategoryUpdateStatus.Field()
    supplier_list_update = SupplierListUpdate.Field()
    supplier_list_update_status = SupplierListUpdateStatus.Field()
    email_list_update = EmailListUpdate.Field()
    email_list_update_status = EmailListUpdateStatus.Field()
    exchange_rate_update = ExchangeRateUpdate.Field()
    coupon_update = CouponUpdate.Field()
    coupon_update_status = CouponUpdateStatus.Field()
    bank_update = BankUpdate.Field()
    bank_update_status = BankUpdateStatus.Field()
    promotion_update_visible = PromotionUpdateVisible.Field()
    voucher_update = VoucherUpdate.Field()
    voucher_update_status = VoucherUpdateStatus.Field()
    buyer_club_voucher_update = BuyerClubVoucherUpdate.Field()
    buyer_club_voucher_update_status = BuyerClubVoucherStatusUpdate.Field()
    warranty_term_update = WarrantyTermUpdate.Field()
    warranty_term_update_status = WarrantyTermUpdateStatus.Field()
    set_product_advertisement_update = SetProductAdvertisementUpdate.Field()
    set_product_advertisement_update_status = SetProductAdvertisementUpdateStatus.Field()

    # --------------------------Delete-------------------------

    reason_delete = ReasonDelete.Field()
    language_delete = LanguageDelete.Field()
    promotion_delete = PromotionDelete.Field()
    country_delete = CountryDelete.Field()
    currency_delete = CurrencyDelete.Field()
    contract_type_delete = ContractTypeDelete.Field()
    payment_term_delete = PaymentTermDelete.Field()
    delivery_term_delete = DeliveryTermDelete.Field()
    unit_of_measure_delete = UnitofMeasureDelete.Field()
    email_templates_delete = EmailTemplatesDelete.Field()
    number_of_employee_delete = NumberofEmployeeDelete.Field()
    gender_delete = GenderDelete.Field()
    technical_weighting_delete = TechnicalWeightingDelete.Field()
    auction_type_delete = AuctionTypeDelete.Field()
    position_delete = PositionDelete.Field()
    level_delete = LevelDelete.Field()
    industry_delete = IndustryDelete.Field()
    industry_cluster_delete = IndustryClusterDelete.Field()
    industry_sectors_delete = IndustrySectorsDelete.Field()
    industry_sub_sector_delete = IndustrySubSectorsDelete.Field()
    client_focus_delete = ClientFocusDelete.Field()
    family_code_delete = FamilyCodeDelete.Field()
    cluster_code_delete = ClusterCodeDelete.Field()
    sub_cluster_code_delete = SubClusterCodeDelete.Field()
    category_delete = CategoryDelete.Field()
    supplier_list_delete = SupplierListDelete.Field()
    email_list_delete = EmailListDelete.Field()
    exchange_rate_delete = ExchangeRateDelete.Field()
    coupon_delete = CouponDelete.Field()
    bank_delete = BankDelete.Field()
    voucher_delete = VoucherDelete.Field()
    buyer_club_voucher_delete = BuyerClubVoucherDelete.Field()
    warranty_term_delete = WarrantyTermDelete.Field()
    set_product_advertisement_delete = SetProductAdvertisementDelete.Field()

    # ---------------------------translation-----------------------------
    country_translation_update = CountryTranslationUpdate.Field()
