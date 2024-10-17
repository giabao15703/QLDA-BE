import django_filters
import graphene
from apps.core import Error, CustomNode, CustomizeFilterConnectionField
from apps.sale_schema.error_code import SaleSchemaError
from apps.sale_schema.models import (
    ProfileFeaturesBuyer,
    ProfileFeaturesSupplier,
    SICPRegistration,
    PlatformFee,
    AuctionFee,
    OurPartner,
)
from apps.users.models import Token
from django_filters import FilterSet, OrderingFilter
from django.utils import timezone
from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

class ProfileFeaturesBuyerFilter(FilterSet):
    id = django_filters.CharFilter(field_name='id', lookup_expr='exact')
    class Meta:
        model = ProfileFeaturesBuyer
        fields =  {
            'id': ['exact']
        }

    order_by = OrderingFilter(fields=('id'))


class ProfileFeaturesBuyerNode(DjangoObjectType):
    class Meta:
        model = ProfileFeaturesBuyer
        filterset_class = ProfileFeaturesBuyerFilter
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = queryset.filter().order_by('id')
        return queryset

class ProfileFeaturesSupplierFilter(FilterSet):
    id = django_filters.CharFilter(field_name='id', lookup_expr='exact')
    class Meta:
        model = ProfileFeaturesSupplier
        fields =  {
            'id': ['exact']
        }

    order_by = OrderingFilter(fields=('id'))

class ProfileFeaturesSupplierNode(DjangoObjectType):
    class Meta:
        model = ProfileFeaturesSupplier
        filterset_class = ProfileFeaturesSupplierFilter
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = queryset.filter().order_by('id')
        return queryset

class SICPRegistrationFilter(FilterSet):
    id = django_filters.CharFilter(field_name='id', lookup_expr='exact')
    class Meta:
        model = ProfileFeaturesSupplier
        fields =  {
            'id': ['exact']
        }

    order_by = OrderingFilter(fields=('id'))

class SICPRegistrationNode(DjangoObjectType):
    class Meta:
        model = SICPRegistration
        filterset_class = SICPRegistrationFilter
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = queryset.filter().order_by('id')
        return queryset


class PlatformFeeFilter(FilterSet):
    class Meta:
        model = PlatformFee
        fields = {
            'id': ['exact'],
            'title': ['icontains'],
            'fee': ['exact'],
        }

    order_by = OrderingFilter(fields=('id', 'title', 'fee'))


class PlatformFeeNode(DjangoObjectType):
    class Meta:
        model = PlatformFee
        filterset_class = PlatformFeeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = queryset.filter().order_by('id')
        return queryset


class AuctionFeeFilter(FilterSet):
    class Meta:
        model = AuctionFee
        fields = {
            'id': ['exact'],
            'min_value': ['exact'],
            'max_value': ['exact'],
            'percentage': ['exact'],
        }

    order_by = OrderingFilter(fields=('id', 'min_value', 'max_value', 'percentage'))


class AuctionFeeNode(DjangoObjectType):
    class Meta:
        model = AuctionFee
        filterset_class = AuctionFeeFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = queryset.filter().order_by('id')
        return queryset


class OurPartnerFilter(FilterSet):
    valid_from = django_filters.DateTimeFilter("valid_from", lookup_expr="gte")
    valid_to = django_filters.DateTimeFilter("valid_to", lookup_expr="lte")

    class Meta:
        model = OurPartner
        fields = {
            'id': ['exact'],
            'title': ['contains'],
            'status': ['exact'],
        }

    order_by = OrderingFilter(fields=('id', 'title', 'status', 'valid_from', 'valid_to'))


class OurPartnerInterface(relay.Node):
    class Meta:
        name = "OurPartnerInterface"

    @classmethod
    def to_global_id(cls, type, id):
        return id

    @staticmethod
    def get_node_from_global_id(info, global_id, only_type=None):
        return OurPartner.objects.get(id=global_id)


class OurPartnerNode(DjangoObjectType):
    class Meta:
        model = OurPartner
        filterset_class = OurPartnerFilter
        interfaces = (OurPartnerInterface,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                queryset = queryset.filter().order_by("id")
            else:
                queryset = queryset.filter(status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()).order_by('id')
        except:
            queryset = queryset.filter(status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now()).order_by('id')
        return queryset

    def resolve_image(self, info):
        if self.image and hasattr(self.image, "url"):
            if self.image.url.lower().replace('/media/', '').startswith("http"):
                return self.image
            else:
                return info.context.build_absolute_uri(self.image.url)
        else:
            return None

    def resolve_logo(self, info):
        if self.logo and hasattr(self.logo, "url"):
            if self.logo.url.lower().replace('/media/', '').startswith("http"):
                return self.logo
            else:
                return info.context.build_absolute_uri(self.logo.url)
        else:
            return None


# -----------------CREATE----------------


class ProfileFeaturesBuyerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    market_research = graphene.String(required=True)
    rfx_year = graphene.Int(required=True)
    no_eauction_year = graphene.Int(required=True)
    help_desk = graphene.String(required=True)
    report_year = graphene.Int(required=True)
    sub_user_accounts = graphene.Int(required=True)
    fee_eauction = graphene.Float()
    total_fee_year = graphene.Float()
    profile_features_type = graphene.Int(required=True)
    status = graphene.Boolean()
    rfx_auto_nego = graphene.Boolean()


class ProfileFeaturesBuyerCreate(graphene.Mutation):
    class Arguments:
        profileFeatures = ProfileFeaturesBuyerInput(required=True)

    status = graphene.Boolean()
    profileFeatures = graphene.Field(ProfileFeaturesBuyerNode)
    error = graphene.Field(Error)

    def mutate(root, info, profileFeatures=None):
        profile_features_instance = ProfileFeaturesBuyer(
            name=profileFeatures.name,
            market_research=profileFeatures.market_research,
            rfx_year=profileFeatures.rfx_year,
            no_eauction_year=profileFeatures.no_eauction_year,
            help_desk=profileFeatures.help_desk,
            report_year=profileFeatures.report_year,
            sub_user_accounts=profileFeatures.sub_user_accounts,
            fee_eauction=profileFeatures.fee_eauction,
            total_fee_year=profileFeatures.total_fee_year,
            profile_features_type=profileFeatures.profile_features_type,
            status=profileFeatures.status,
            rfx_auto_nego=profileFeatures.rfx_auto_nego,
        )
        profile_features_instance.save()
        return ProfileFeaturesBuyerCreate(status=True, profileFeatures=profile_features_instance)


class ProfileFeaturesSupplierInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    free_registration = graphene.String(required=True)
    quote_submiting = graphene.String(required=True)
    rfxr_receiving_priority = graphene.Int(required=True)
    sub_user_accounts = graphene.Int(required=True)
    help_desk = graphene.String(required=True)
    flash_sale = graphene.Int(required=True)
    report_year = graphene.Int(required=True)
    base_rate_month = graphene.Float(required=True)
    base_rate_full_year = graphene.Float(required=True)
    profile_features_type = graphene.Int(required=True)
    status = graphene.Boolean()
    product = graphene.Int()


class ProfileFeaturesSupplierCreate(graphene.Mutation):
    class Arguments:
        profileFeatures = ProfileFeaturesSupplierInput(required=True)

    status = graphene.Boolean()
    profileFeatures = graphene.Field(ProfileFeaturesSupplierNode)

    def mutate(root, info, profileFeatures=None):
        profile_features_instance = ProfileFeaturesSupplier(
            name=profileFeatures.name,
            free_registration=profileFeatures.free_registration,
            quote_submiting=profileFeatures.quote_submiting,
            rfxr_receiving_priority=profileFeatures.rfxr_receiving_priority,
            sub_user_accounts=profileFeatures.sub_user_accounts,
            help_desk=profileFeatures.help_desk,
            flash_sale=profileFeatures.flash_sale,
            report_year=profileFeatures.report_year,
            base_rate_month=profileFeatures.base_rate_month,
            base_rate_full_year=profileFeatures.base_rate_full_year,
            profile_features_type=profileFeatures.profile_features_type,
            status=profileFeatures.status,
        )
        profile_features_instance.save()
        return ProfileFeaturesSupplierCreate(status=True, profileFeatures=profile_features_instance)


class SICPRegistrationInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    legal_status = graphene.Float()
    bank_account = graphene.Float()
    sanction_check = graphene.Float()
    certificate_management = graphene.Float()
    due_diligence = graphene.Float()
    financial_risk = graphene.Float()
    total_amount = graphene.Float()
    sicp_type = graphene.Float()
    status = graphene.Boolean()


class SICPRegistrationCreate(graphene.Mutation):
    class Arguments:
        sicp_registration = SICPRegistrationInput(required=True)

    status = graphene.Boolean()
    sicp_registration = graphene.Field(SICPRegistrationNode)
    error = graphene.Field(Error)

    def mutate(root, info, sicp_registration=None):
        sicp_registration_instance = SICPRegistration(
            name=sicp_registration.name,
            legal_status=sicp_registration.legal_status,
            bank_account=sicp_registration.bank_account,
            sanction_check=sicp_registration.sanction_check,
            certificate_management=sicp_registration.certificate_management,
            due_diligence=sicp_registration.due_diligence,
            financial_risk=sicp_registration.financial_risk,
            total_amount=sicp_registration.total_amount,
            sicp_type=sicp_registration.sicp_type,
            status=sicp_registration.status,
        )
        sicp_registration_instance.save()
        return SICPRegistrationCreate(status=True, sicp_registration=sicp_registration_instance)


class PlatformFeeCreate(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        fee = graphene.Float(required=True)

    status = graphene.Boolean()
    platform_fee = graphene.Field(PlatformFeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, title, fee):
        platform_fee = PlatformFee.objects.create(title=title, fee=fee)
        return PlatformFeeCreate(status=True, platform_fee=platform_fee)


class AuctionFeeInput(graphene.InputObjectType):
    min_value = graphene.Float()
    max_value = graphene.Float()
    percentage = graphene.Float()


class AuctionFeeCreate(graphene.Mutation):
    class Arguments:
        auction_fee = AuctionFeeInput(required=True)

    status = graphene.Boolean()
    auction_fee = graphene.Field(AuctionFeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, auction_fee=None):
        if auction_fee.percentage < 0 or auction_fee.percentage > 100:
            error = Error(code="SALE_SCHEMA_01", message=SaleSchemaError.SALE_SCHEMA_01)
            return AuctionFeeCreate(status=False, error=error)

        auction_fee_instance = AuctionFee(min_value=auction_fee.min_value, max_value=auction_fee.max_value, percentage=auction_fee.percentage)

        if auction_fee.min_value >= auction_fee.max_value:
            error = Error(code="SALE_SCHEMA_02", message=SaleSchemaError.SALE_SCHEMA_02)
            return AuctionFeeCreate(status=False, error=error)

        ob = AuctionFee.objects.all()
        for x in ob:
            if x.min_value <= auction_fee.min_value <= x.max_value or x.min_value <= auction_fee.max_value <= x.max_value:
                error = Error(code="SALE_SCHEMA_03", message=SaleSchemaError.SALE_SCHEMA_03)
                return AuctionFeeCreate(status=False, error=error)

            elif x.min_value >= auction_fee.min_value and auction_fee.max_value >= x.max_value:
                error = Error(code="SALE_SCHEMA_03", message=SaleSchemaError.SALE_SCHEMA_03)
                return AuctionFeeCreate(status=False, error=error)

        auction_fee_instance.save()
        return AuctionFeeCreate(status=True, auction_fee=auction_fee_instance)


class OurPartnerInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    image = Upload(required=True)
    status = graphene.Boolean(required=True)
    valid_from = graphene.DateTime(required=True)
    valid_to = graphene.DateTime(required=True)
    logo = Upload()
    link = graphene.String()
    description = graphene.String()

class OurPartnerCreate(graphene.Mutation):
    class Arguments:
        input = OurPartnerInput(required=True)

    status = graphene.Boolean()
    our_partner = graphene.Field(OurPartnerNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        if input.valid_from >= input.valid_to:
            raise GraphQLError("Invalid Date")
        our_partner = OurPartner.objects.create(**input)
        return OurPartnerCreate(status=True, our_partner=our_partner)


# -----------------UPDATE----------------


class ProfileFeaturesBuyerUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ProfileFeaturesBuyerInput(required=True)

    status = graphene.Boolean(default_value=False)
    profile_features_buyer = graphene.Field(ProfileFeaturesBuyerNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        authorization_header = info.context.headers.get('Authorization')
        if not authorization_header:
            return ProfileFeaturesBuyerUpdate(error=Error(code="SALE_SCHEMA_05", message=SaleSchemaError.SALE_SCHEMA_05))
        key = authorization_header.split(" ")[-1]
        token = Token.objects.get(key=key)
        if not token.user.isAdmin():
            return ProfileFeaturesBuyerUpdate(error=Error(code="SALE_SCHEMA_05", message=SaleSchemaError.SALE_SCHEMA_05))
        status = False
        profile_features_buyer_instance = ProfileFeaturesBuyer.objects.get(pk=id)
        if profile_features_buyer_instance:
            status = True
            profile_features_buyer_instance.name = input.name
            profile_features_buyer_instance.market_research = input.market_research
            profile_features_buyer_instance.rfx_year = input.rfx_year
            profile_features_buyer_instance.no_eauction_year = input.no_eauction_year
            profile_features_buyer_instance.help_desk = input.help_desk
            profile_features_buyer_instance.report_year = input.report_year
            profile_features_buyer_instance.sub_user_accounts = input.sub_user_accounts
            profile_features_buyer_instance.fee_eauction = input.fee_eauction
            profile_features_buyer_instance.total_fee_year = input.total_fee_year
            profile_features_buyer_instance.profile_features_type = input.profile_features_type
            profile_features_buyer_instance.status = input.status
            if input.get("rfx_auto_nego") is not None:
                profile_features_buyer_instance.rfx_auto_nego = input.rfx_auto_nego
            profile_features_buyer_instance.save()
            return ProfileFeaturesBuyerUpdate(status=status, profile_features_buyer=profile_features_buyer_instance)
        return ProfileFeaturesBuyerUpdate(status=status, profile_features_buyer=None)


class ProfileFeaturesSupplierUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ProfileFeaturesSupplierInput(required=True)

    status = graphene.Boolean()
    profile_features_supplier = graphene.Field(ProfileFeaturesSupplierNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input=None):
        authorization_header = info.context.headers.get('Authorization')
        if not authorization_header:
            return ProfileFeaturesSupplierUpdate(error=Error(code="SALE_SCHEMA_05", message=SaleSchemaError.SALE_SCHEMA_05))
        key = authorization_header.split(" ")[-1]
        token = Token.objects.get(key=key)
        if not token.user.isAdmin():
            return ProfileFeaturesSupplierUpdate(error=Error(code="SALE_SCHEMA_05", message=SaleSchemaError.SALE_SCHEMA_05))
        status = False
        profile_features_supplier_instance = ProfileFeaturesSupplier.objects.get(pk=id)
        if profile_features_supplier_instance:
            status = True
            profile_features_supplier_instance.name = input.name
            profile_features_supplier_instance.free_registration = input.free_registration
            profile_features_supplier_instance.quote_submiting = input.quote_submiting
            profile_features_supplier_instance.rfxr_receiving_priority = input.rfxr_receiving_priority
            profile_features_supplier_instance.sub_user_accounts = input.sub_user_accounts
            profile_features_supplier_instance.help_desk = input.help_desk
            profile_features_supplier_instance.flash_sale = input.flash_sale
            profile_features_supplier_instance.report_year = input.report_year
            profile_features_supplier_instance.base_rate_month = input.base_rate_month
            profile_features_supplier_instance.base_rate_full_year = input.base_rate_full_year
            profile_features_supplier_instance.profile_features_type = input.profile_features_type
            profile_features_supplier_instance.status = input.status
            profile_features_supplier_instance.product = input.product if input.product is not None else profile_features_supplier_instance.product
            profile_features_supplier_instance.save()
            return ProfileFeaturesSupplierUpdate(status=status, profile_features_supplier=profile_features_supplier_instance)
        return ProfileFeaturesSupplierUpdate(status=status, profile_features_supplier=None)

class ProfileFeaturesSupplierFlashSaleUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        number_of_flash_sale = graphene.Int(required=True)

    status = graphene.Boolean()
    profile_features_supplier = graphene.Field(ProfileFeaturesSupplierNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, number_of_flash_sale):
        status = False
        profile_features_supplier_instance = ProfileFeaturesSupplier.objects.get(pk=id)
        if profile_features_supplier_instance:
            status = True
            profile_features_supplier_instance.flash_sale = number_of_flash_sale
            profile_features_supplier_instance.save()
            return ProfileFeaturesSupplierFlashSaleUpdate(status=status, profile_features_supplier=profile_features_supplier_instance)
        return ProfileFeaturesSupplierFlashSaleUpdate(status=status, profile_features_supplier=None)


class SICPRegistrationUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = SICPRegistrationInput(required=True)

    status = graphene.Boolean()
    sicp_registration = graphene.Field(SICPRegistrationNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input=None):
        status = False
        sicp_registration_instance = SICPRegistration.objects.get(pk=id)
        if sicp_registration_instance:
            status = True
            sicp_registration_instance.name = input.name
            sicp_registration_instance.legal_status = input.legal_status
            sicp_registration_instance.bank_account = input.bank_account
            sicp_registration_instance.sanction_check = input.sanction_check
            sicp_registration_instance.certificate_management = input.certificate_management
            sicp_registration_instance.due_diligence = input.due_diligence
            sicp_registration_instance.financial_risk = input.financial_risk
            sicp_registration_instance.total_amount = input.total_amount
            sicp_registration_instance.sicp_type = input.sicp_type
            sicp_registration_instance.status = input.status
            sicp_registration_instance.save()
            return SICPRegistrationUpdate(status=status, sicp_registration=sicp_registration_instance)
        return SICPRegistrationUpdate(status=status, sicp_registration=None)


class PlatformFeeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        title = graphene.String(required=True)
        fee = graphene.Float(required=True)

    status = graphene.Boolean()
    platform_fee = graphene.Field(PlatformFeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, title, fee):
        platform_fee = PlatformFee.objects.filter(id=id).first()
        platform_fee.title = title
        platform_fee.fee = fee
        platform_fee.save()
        return PlatformFeeUpdate(status=True, platform_fee=platform_fee)


class AuctionFeeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = AuctionFeeInput(required=True)

    status = graphene.Boolean()
    auction_fee = graphene.Field(AuctionFeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input=None):
        if input.percentage < 0 or input.percentage > 100:
            error = Error(code="SALE_SCHEMA_01", message=SaleSchemaError.SALE_SCHEMA_01)
            return AuctionFeeUpdate(status=False, error=error)

        status = False
        auction_fee_instance = AuctionFee.objects.get(pk=id)
        if auction_fee_instance:
            status = True
            if input.min_value >= input.max_value:
                error = Error(code="SALE_SCHEMA_04", message=SaleSchemaError.SALE_SCHEMA_04)
                return AuctionFeeUpdate(status=False, error=error)

            ob = AuctionFee.objects.all().exclude(id=id)
            for x in ob:
                if x.min_value <= input.min_value <= x.max_value or x.min_value <= input.max_value <= x.max_value:
                    error = Error(code="SALE_SCHEMA_03", message=SaleSchemaError.SALE_SCHEMA_03)
                    return AuctionFeeUpdate(status=False, error=error)

                elif x.min_value >= input.min_value and input.max_value >= x.max_value:
                    error = Error(code="SALE_SCHEMA_03", message=SaleSchemaError.SALE_SCHEMA_03)
                    return AuctionFeeUpdate(status=False, error=error)

            auction_fee_instance.min_value = input.min_value
            auction_fee_instance.max_value = input.max_value
            auction_fee_instance.percentage = input.percentage
            auction_fee_instance.save()
            return AuctionFeeUpdate(status=status, auction_fee=auction_fee_instance)
        return AuctionFeeUpdate(status=status, auction_fee=None)


class OurPartnerUpdateInput(graphene.InputObjectType):
    title = graphene.String()
    image = Upload()
    valid_from = graphene.DateTime()
    valid_to = graphene.DateTime()
    status = graphene.Boolean()
    logo = Upload()
    link = graphene.String()
    description = graphene.String()

class OurPartnerUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = OurPartnerUpdateInput(required=True)

    status = graphene.Boolean()
    our_partner = graphene.Field(OurPartnerNode)
    error = graphene.Field(Error)

    def mutate(root, info, input, id):
        our_partner = OurPartner.objects.get(id=id)
        if input.valid_from and input.valid_to and input.valid_from >= input.valid_to:
            raise GraphQLError("Invalid Date")
        elif input.valid_from and input.valid_from >= our_partner.valid_to:
            raise GraphQLError("Invalid Date")
        elif input.valid_to and input.valid_to <= our_partner.valid_from:
            raise GraphQLError("Invalid Date")
        for key, values in input.items():
            if key in [f.name for f in OurPartner._meta.get_fields()]:
                setattr(our_partner, key, values)
        our_partner.save()
        return OurPartnerUpdate(status=True, our_partner=our_partner)


class OurPartnerStatusInput(graphene.InputObjectType):
    our_partner_id = graphene.String(required=True)
    status = graphene.Boolean(required=True)


class OurPartnerUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(OurPartnerStatusInput, required=True)

    def mutate(root, info, list_status):
        for our_partner in list_status:
            partner = OurPartner.objects.get(id=our_partner.our_partner_id)
            partner.status = our_partner.status
            partner.save()
        return OurPartnerUpdateStatus(status=True)


# -----------------DELETE----------------


class ProfileFeaturesBuyerDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        profile_features_buyer_instance = ProfileFeaturesBuyer.objects.get(pk=id)
        profile_features_buyer_instance.delete()
        return ProfileFeaturesBuyerDelete(status=True)


class ProfileFeaturesSupplierDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        profile_features_supplier_instance = ProfileFeaturesSupplier.objects.get(pk=id)
        profile_features_supplier_instance.delete()
        return ProfileFeaturesSupplierDelete(status=True)


class PlatformFeeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id):
        platform_fee = PlatformFee.objects.get(pk=id).delete()
        return PlatformFeeDelete(status=True)


class AuctionFeeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        auction_fee_instance = AuctionFee.objects.get(pk=id)
        auction_fee_instance.delete()
        return AuctionFeeDelete(status=True)


class OurPartnerDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id):
        our_partner = OurPartner.objects.get(id=id).delete()
        return OurPartnerDelete(status=True)


# -----------------MUTATION----------------


class Mutation(graphene.ObjectType):
    profile_features_buyer_create = ProfileFeaturesBuyerCreate.Field()
    profile_features_supplier_create = ProfileFeaturesSupplierCreate.Field()
    sicp_registration_create = SICPRegistrationCreate.Field()
    platform_fee_create = PlatformFeeCreate.Field()
    auction_fee_create = AuctionFeeCreate.Field()
    our_partner_create = OurPartnerCreate.Field()

    profile_features_buyer_update = ProfileFeaturesBuyerUpdate.Field()
    profile_features_supplier_update = ProfileFeaturesSupplierUpdate.Field()
    profile_features_supplier_flash_sale_update = ProfileFeaturesSupplierFlashSaleUpdate.Field()
    sicp_registration_update = SICPRegistrationUpdate.Field()
    platform_fee_update = PlatformFeeUpdate.Field()
    auction_fee_update = AuctionFeeUpdate.Field()
    our_partner_update = OurPartnerUpdate.Field()

    profile_features_buyer_delete = ProfileFeaturesBuyerDelete.Field()
    profile_features_supplier_delete = ProfileFeaturesBuyerDelete.Field()
    platform_fee_delete = PlatformFeeDelete.Field()
    auction_fee_delete = AuctionFeeDelete.Field()
    our_partner_delete = OurPartnerDelete.Field()
    our_partner_update_status = OurPartnerUpdateStatus.Field()

# -----------------QUERY----------------


class Query(ObjectType):
    profile_features_buyer = CustomNode.Field(ProfileFeaturesBuyerNode)
    profile_features_buyer = CustomizeFilterConnectionField(ProfileFeaturesBuyerNode)

    profile_features_supplier = CustomNode.Field(ProfileFeaturesSupplierNode)
    profile_features_supplier = CustomizeFilterConnectionField(ProfileFeaturesSupplierNode)

    sicp_registration = CustomNode.Field(SICPRegistrationNode)
    sicp_registration = CustomizeFilterConnectionField(SICPRegistrationNode)

    platform_fee = CustomNode.Field(PlatformFeeNode)
    platform_fees = CustomizeFilterConnectionField(PlatformFeeNode)

    auction_fee = CustomNode.Field(AuctionFeeNode)
    auction_fees = CustomizeFilterConnectionField(AuctionFeeNode)

    our_partner = OurPartnerInterface.Field(OurPartnerNode)
    our_partners = CustomizeFilterConnectionField(OurPartnerNode)
    