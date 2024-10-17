import datetime
import filetype
import graphene
import re

from django.db.models import Subquery

from apps.users.models import (
    Buyer,
    User,
    BuyerIndustry,
    Supplier,
    SupplierIndustry,
    SupplierClientFocus,
    SupplierCategory,
    SupplierCompanyCredential,
    SupplierBusinessLicense,
    SupplierFormRegistrations,
    SupplierQualityCertification,
    SupplierTaxCertification,
    SupplierOthers,
    SupplierBankCertification,
    SupplierPortfolio,
    BuyerSubAccounts,
    SupplierSubAccount,
    SupplierSubAccountActivity,
    UserDiamondSponsor,
    Token,
    SupplierSICP,
    SupplierSICPFile,
    SICPTextEditor,
    SICPTextEditorFile,
    UserDiamondSponsorFee,
    SupplierFlashSale,
    ProductType,
    SupplierProduct,
    ProductConfirmStatus,
    SupplierProductImage,
    SupplierProductFlashSale,
    SupplierProductWholesalePrice,
    RelatedSupplierProduct,
    ProductInventoryStatus,
    SupplierProductCategory,
    SupplierCertificate,
    SupplierCertificateType,
    UserFollowingSupplierStatus,
    UserFollowingSupplier,
    UserRatingSupplierProduct,
)
from apps.users.schema import (
    BuyerNode,
    GetToken,
    SupplierNode,
    SupplierIndustryInput,
    ClientFocusInputSupplier,
    PortfoliosUpdateInput,
    CategorySupplierInput,
    SupplierSubAccountNode,
    UserDiamondSponsorNode,
    SupplierSICPNode,
    SICPTextEditorNode,
    UserDiamondSponsorFeeNode,
    SupplierFlashSaleNode,
    SupplierProductNode,
    UserFollowingSupplierNode,
    UserRatingSupplierProductNode,
)

from apps.master_data.models import (
    Category,
    Country,
    CountryState,
    Currency,
    NumberofEmployee,
    Position,
    Language,
    PaymentTerm,
    Gender,
    Promotion,
    UnitofMeasure,
    EmailTemplates,
    EmailTemplatesTranslation,
)
from apps.payment.models import UserPayment
from apps.sale_schema.models import ProfileFeaturesBuyer, ProfileFeaturesSupplier, SICPRegistration
from apps.payment.schema import send_mail_upgraded, send_mail_sicp
from apps.users.error_code import UserError
from apps.core import Error
from django.core.mail import send_mail
from django.db import transaction
from django.template import Template, Context
from django.utils import timezone
from graphene_django_plus.mutations import ModelUpdateMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from PyPDF2 import PdfFileReader


def convert_size(bytes_size: float):
    if bytes_size < 1024:
        return str(bytes_size) + " bytes"
    elif bytes_size < (1024 * 1024):
        return str(round(bytes_size / 1024)) + " KB"
    elif bytes_size < (1024 * 1024 * 1024):
        return str(round(bytes_size / (1024 * 1024))) + " MB"
    else:
        return str(round(bytes_size / (1024 * 1024 * 1024))) + " GB"


def is_pdf(file):
    try:
        pdf = PdfFileReader(file)
        return True
    except:
        return False


class UserBasicInput(graphene.InputObjectType):
    password = graphene.String(required=True)
    email = graphene.String(required=True)
    full_name = graphene.String(required=True)


# ----------------------------------------------------Buyer-----------------------------------------------------------------


class BuyerBasicInput(graphene.InputObjectType):
    company_full_name = graphene.String(required=True)
    company_logo = Upload()
    company_tax = graphene.String(required=True)
    company_address = graphene.String(required=True)
    company_city = graphene.String(required=True)
    company_country = graphene.String(required=True)
    company_country_state = graphene.String(required=True)
    company_number_of_employee = graphene.String(required=True)
    company_website = graphene.String(required=False)
    company_referral_code = graphene.String(required=False)
    gender = graphene.String(required=True)
    picture = Upload()
    phone = graphene.String(required=True)
    position = graphene.String(required=True)
    currency = graphene.String(required=True)
    language = graphene.String(required=True)
    user = graphene.Field(UserBasicInput, required=True)
    industries = graphene.List(graphene.String, required=True)


class BuyerRegister(graphene.Mutation):
    status = graphene.Boolean()
    buyer = graphene.Field(BuyerNode)
    error = graphene.Field(Error)

    class Arguments:

        input = BuyerBasicInput(required=True)

    def mutate(root, info, input):
        try:
            error = None
            if (User.objects.filter(user_type=2, email=input.user.email)).exists():
                error = Error(code="USER_01", message=UserError.USER_01)
                raise GraphQLError('USER_01')
            if len(input.company_referral_code) > 0:
                promo = Promotion.objects.filter(name=input.company_referral_code, status=True)
                if not promo.exists():
                    error = Error(code="USER_34", message=UserError.USER_34)
                    raise GraphQLError('USER_34')
            if not re.search("^(.*)(([A-Z]+.*[0-9]+)|([0-9]+.*[A-Z]+))(.*){8,16}$", input.user.password):
                error = Error(code="USER_35", message=UserError.USER_35)
                raise GraphQLError('USER_35')
            user_count = User.objects.filter(user_type=2, company_position=1).count() + 1
            username = '80' + str(user_count).zfill(4)
            language_id = input.language
            user = User(username=username, user_type=2, language_id=language_id, **input.user)
            user.set_password(input.user.password)
            user.save()
            profile_features = ProfileFeaturesBuyer.objects.filter(profile_features_type=1).first()
            buyer = Buyer.objects.create(
                company_full_name=input.company_full_name,
                company_logo=input.company_logo,
                company_tax=input.company_tax,
                company_address=input.company_address,
                company_city=input.company_city,
                company_country_id=input.company_country,
                company_country_state_id=input.company_country_state,
                company_number_of_employee_id=input.company_number_of_employee,
                company_website=input.company_website,
                company_referral_code=input.company_referral_code,
                gender_id=input.gender,
                picture=input.picture,
                phone=input.phone,
                language_id=language_id,
                position_id=input.position,
                currency_id=input.currency,
                user=user,
                profile_features=profile_features,
            )
            UserPayment.objects.create(user=user)
            if len(input.industries) == 0:
                error = Error(code="USER_03", message=UserError.USER_03)
                raise GraphQLError("USER_03")
            if len(input.industries) > 10:
                error = Error(code="USER_04", message=UserError.USER_04)
                raise GraphQLError("USER_04")

            for industry_id in input.industries:
                buyer_industry = BuyerIndustry.objects.create(industry_id=industry_id, user_buyer=buyer)

            email = EmailTemplatesTranslation.objects.filter(email_templates__item_code="ActivateBuyerAccount", language_code=user.language.item_code)
            if not email:
                email = EmailTemplates.objects.filter(item_code="ActivateBuyerAccount")
            email = email.first()
            messages = Template(email.content).render(
                Context(
                    {
                        "image": info.context.build_absolute_uri("/static/logo_mail.png"),
                        "name": user.full_name,
                        "username": user.username,
                        "password": input.user.password,
                    }
                )
            )
            try:
                send_mail(email.title, messages, "NextPro <no-reply@nextpro.io>", [user.email], html_message=messages, fail_silently=True)
            except:
                print("Fail mail")
            return BuyerRegister(status=True, buyer=buyer)
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return BuyerRegister(error=error, status=False)


class BuyerDetailUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Meta:
        model = Buyer
        exclude_fields = [
            'id',
            'user',
            'valid_from',
            'valid_to',
            'company_logo',
            'level',
            'picture',
            'send_mail_30_day',
            'send_mail_15_day',
            'send_mail_7_day',
            'send_mail_expire',
        ]
        allow_unauthenticated = True

    class Input:
        full_name = graphene.String()
        company_logo = Upload()
        picture = Upload()
        industries = graphene.List(graphene.String)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
            buyer = user.buyer
            send_mail_check = None
            for key, values in data.items():
                if key in [f.name for f in User._meta.get_fields()]:
                    if key == "language":
                        key = "language_id"
                        values = Language.objects.get(id=values)
                        values = values.id
                    setattr(user, key, values)
                if key == "language_id":
                    key = "language"
                if key in [f.name for f in Buyer._meta.get_fields()]:
                    if key == "currency":
                        values = Currency.objects.get(id=values)
                    elif key == "gender":
                        values = Gender.objects.get(id=values)
                    elif key == "position":
                        values = Position.objects.get(id=values)
                    elif key == "company_number_of_employee":
                        values = NumberofEmployee.objects.get(id=values)
                    elif key == "company_country":
                        values = Country.objects.get(id=values)
                    elif key == "company_country_state":
                        values = CountryState.objects.get(id=values)
                    elif key == "language":
                        values = Language.objects.get(id=values)
                    elif key == "picture":
                        if values is None:
                            values = buyer.picture
                    elif key == "company_logo":
                        if values is None:
                            values = buyer.company_logo
                    elif key == "promotion":
                        values = Promotion.objects.get(id=values)
                    elif (
                            key == "profile_features"
                            and data.get('promotion') is not None
                            and Promotion.objects.get(id=data.get('promotion')).discount == 100
                    ):
                        values = ProfileFeaturesBuyer.objects.filter(id=values).first()
                        send_mail_check = values
                        buyer.valid_from = timezone.now()
                        buyer.valid_to = timezone.now() + timezone.timedelta(days=365)
                        buyer.send_mail_30_day = None
                        buyer.send_mail_15_day = None
                        buyer.send_mail_7_day = None
                        buyer.send_mail_expire = None
                    elif key == "profile_features":
                        values = buyer.profile_features

                    setattr(buyer, key, values)

                if key == "industries":
                    if len(values) == 0:
                        error = Error(code="USER_03", message=UserError.USER_03)
                        raise GraphQLError("USER_03")
                    if len(values) > 10:
                        error = Error(code="USER_04", message=UserError.USER_04)
                        raise GraphQLError("USER_04")
                    buyer_industry_mapping = map(lambda x: x.get('industry_id'), BuyerIndustry.objects.filter(user_buyer=buyer).values('industry_id'))
                    buyer_industry_list = map(lambda x: int(x), values)
                    buyer_industry_list = set(buyer_industry_list)
                    buyer_industry_mapping = set(buyer_industry_mapping)
                    buyer_industry_delete = buyer_industry_mapping.difference(buyer_industry_list)
                    BuyerIndustry.objects.filter(industry_id__in=buyer_industry_delete, user_buyer=buyer).delete()

                    buyer_industry_create = buyer_industry_list.difference(buyer_industry_mapping)
                    for industry_id in buyer_industry_create:
                        industry_buyer = BuyerIndustry.objects.create(industry_id=industry_id, user_buyer=buyer)
            user.save()
            buyer.save()
            if send_mail_check is not None:
                send_mail_upgraded(user, send_mail_check)
            return BuyerDetailUpdate(status=True, buyer=buyer)
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return BuyerDetailUpdate(error=error, status=False)


class BuyerSubAccountsProfileUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Meta:
        model = BuyerSubAccounts
        exclude_fields = ['id', 'user', 'picture', 'buyer']
        allow_unauthenticated = True

    class Input:
        full_name = graphene.String()
        picture = Upload()

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)

            buyer_sub_accounts = BuyerSubAccounts.objects.get(user=user)
            for key, values in data.items():
                if key in [f.name for f in User._meta.get_fields()]:
                    if key == "language":
                        key = "language_id"
                        values = Language.objects.get(id=values)
                        values = values.id
                    setattr(user, key, values)
                if key == "language_id":
                    key = "language"
                if key in [f.name for f in BuyerSubAccounts._meta.get_fields()]:
                    if key == "currency":
                        values = Currency.objects.get(id=values)
                    elif key == "gender":
                        values = Gender.objects.get(id=values)
                    elif key == "position":
                        values = Position.objects.get(id=values)
                    elif key == "language":
                        values = Language.objects.get(id=values)
                    setattr(buyer_sub_accounts, key, values)
            user.save()
            buyer_sub_accounts.save()
            return BuyerSubAccountsProfileUpdate(status=True, buyerSubAccounts=buyer_sub_accounts)
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return BuyerSubAccountsProfileUpdate(error=error, status=False)


class BuyerSubAccountsUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Meta:
        model = BuyerSubAccounts
        exclude_fields = ['user', 'picture', 'buyer']
        allow_unauthenticated = True

    class Input:
        full_name = graphene.String()
        email = graphene.String()
        picture = Upload()

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
            if user.isBuyer() and user.company_position == 1:
                buyer_sub_accounts = BuyerSubAccounts.objects.get(id=data.get('id'))
                if (User.objects.filter(user_type=2, email=data.get("email")).exclude(id=buyer_sub_accounts.user.id)).exists():
                    error = Error(code="USER_01", message=UserError.USER_01)
                    raise GraphQLError('USER_01')
                data.pop('id')
                user_sub = buyer_sub_accounts.user
                for key, values in data.items():
                    if key in [f.name for f in User._meta.get_fields()]:
                        if key == "language":
                            key = "language_id"
                            values = Language.objects.get(id=values)
                            values = values.id
                        setattr(user_sub, key, values)
                    if key == "language_id":
                        key = "language"
                    if key in [f.name for f in BuyerSubAccounts._meta.get_fields()]:
                        if key == "currency":
                            values = Currency.objects.get(id=values)
                        elif key == "gender":
                            values = Gender.objects.get(id=values)
                        elif key == "position":
                            values = Position.objects.get(id=values)
                        elif key == "language":
                            values = Language.objects.get(id=values)
                        setattr(buyer_sub_accounts, key, values)
                user_sub.save()
                buyer_sub_accounts.save()
                return BuyerSubAccountsUpdate(status=True, buyerSubAccounts=buyer_sub_accounts)
            else:
                raise GraphQLError("USER_10")
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return BuyerSubAccountsUpdate(error=error, status=False)


# ----------------------------------------------------Suppler-----------------------------------------------------------------


class SupplierBasicInput(graphene.InputObjectType):
    company_full_name = graphene.String(required=True)
    company_logo = Upload()
    company_tax = graphene.String(required=True)
    company_address = graphene.String(required=True)
    company_city = graphene.String(required=True)
    company_country = graphene.String(required=True)
    company_country_state = graphene.String(required=True)
    company_number_of_employee = graphene.String(required=True)
    company_website = graphene.String(required=False)
    gender = graphene.String(required=True)
    picture = Upload()
    language = graphene.String(required=True)
    phone = graphene.String(required=True)
    position = graphene.String(required=True)
    currency = graphene.String(required=True)
    user = graphene.Field(UserBasicInput, required=True)
    company_credential_profiles = graphene.List(Upload, required=True)
    company_referral_code = graphene.String(required=False)


class SupplierRegister(graphene.Mutation):
    supplier = graphene.Field(SupplierNode)
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:

        input = SupplierBasicInput(required=True)

    def mutate(root, info, input):
        try:
            error = None
            if (User.objects.filter(user_type=3, email=input.user.email)).exists():
                error = Error(code="USER_01", message=UserError.USER_01)
                raise GraphQLError('USER_01')

            if Supplier.objects.filter(company_tax=input.company_tax).exists():
                error = Error(code="USER_33", message=UserError.USER_33)
                raise GraphQLError('USER_33')

            if len(input.company_referral_code) > 0:
                promo = Promotion.objects.filter(name=input.company_referral_code, status=True)
                if not promo.exists():
                    error = Error(code="USER_34", message=UserError.USER_34)
                    raise GraphQLError('USER_34')

            if not re.search("^(.*)(([A-Z]+.*[0-9]+)|([0-9]+.*[A-Z]+))(.*){8,16}$", input.user.password):
                error = Error(code="USER_35", message=UserError.USER_35)
                raise GraphQLError('USER_35')

            user_count = User.objects.filter(user_type=3).count() + 1
            username = '90' + str(user_count).zfill(4)
            language_id = input.language
            user = User(username=username, user_type=3, language_id=language_id, **input.user)
            user.set_password(input.user.password)
            user.save()
            profile_features = ProfileFeaturesSupplier.objects.filter(profile_features_type=1).first()
            sicp_registration = SICPRegistration.objects.filter(sicp_type=1).first()
            supplier = Supplier.objects.create(
                company_full_name=input.company_full_name,
                company_logo=input.company_logo,
                company_tax=input.company_tax,
                company_address=input.company_address,
                company_city=input.company_city,
                company_country_id=input.company_country,
                company_country_state_id=input.company_country_state,
                company_number_of_employee_id=input.company_number_of_employee,
                company_website=input.company_website,
                gender_id=input.gender,
                picture=input.picture,
                phone=input.phone,
                language_id=input.language,
                position_id=input.position,
                currency_id=input.currency,
                user=user,
                profile_features=profile_features,
                sicp_registration=sicp_registration,
                company_referral_code=input.company_referral_code,
            )
            UserPayment.objects.create(user=user)
            for company_credential in input.company_credential_profiles:
                SupplierCompanyCredential.objects.create(supplier=supplier, company_credential_profile=company_credential)

            email = EmailTemplatesTranslation.objects.filter(
                email_templates__item_code="ActivateSupplierAccount", language_code=user.language.item_code
            )
            if not email:
                email = EmailTemplates.objects.filter(item_code="ActivateSupplierAccount")
            email = email.first()

            messages = Template(email.content).render(
                Context(
                    {
                        "image": info.context.build_absolute_uri("/static/logo_mail.png"),
                        "name": user.full_name,
                        "username": user.username,
                        "password": input.user.password,
                    }
                )
            )
            try:
                send_mail(email.title, messages, "NextPro <no-reply@nextpro.io>", [user.email], html_message=messages, fail_silently=True)
            except:
                print("Fail mail")
            return SupplierRegister(status=True, supplier=supplier)
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return SupplierRegister(status=False, error=error)


class SupplierDetailUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Meta:
        model = Supplier
        exclude_fields = [
            'id',
            'user',
            'valid_from',
            'valid_to',
            'company_logo',
            'company_credential_profile',
            'level',
            'picture',
            'supplier_form_registrationss',
            'bank_certification',
            'quality_certification',
            'business_license',
            'tax_certification',
            'others',
            'send_mail_30_day',
            'send_mail_15_day',
            'send_mail_7_day',
            'send_mail_expire',
        ]
        allow_unauthenticated = True

    class Input:
        full_name = graphene.String()
        email = graphene.String()
        company_logo = Upload()
        picture = Upload()
        image_banner = Upload()
        company_credential_profiles = graphene.List(Upload)

        form_registrations = graphene.List(Upload)
        bank_certifications = graphene.List(Upload)
        quality_certifications = graphene.List(Upload)
        business_licenses = graphene.List(Upload)
        tax_certifications = graphene.List(Upload)
        other = graphene.List(Upload)

        core_business = graphene.List(graphene.List(CategorySupplierInput))
        industries = graphene.List(SupplierIndustryInput)
        client_focus = graphene.List(ClientFocusInputSupplier)
        portfolios = graphene.List(PortfoliosUpdateInput)
        portfolios_delete = graphene.List(graphene.String)

        certificate_list = graphene.List(Upload)
        certificate_remove = graphene.List(graphene.String)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)

            supplier = user.supplier
            profile_features = None
            sicp_registration = None
            if "certificate_remove" in data and data.get("certificate_remove") and not all(SupplierCertificate.objects.filter(user_supplier=supplier, id=x).exists() for x in data.get("certificate_remove")):
                error = Error(code="USER_30", message=UserError.USER_30)
                return SupplierDetailUpdate(error=error, status=False)
            for key, values in data.items():
                if key in [f.name for f in User._meta.get_fields()]:
                    if key == "language":
                        key = "language_id"
                        values = Language.objects.get(id=values)
                        values = values.id
                    setattr(user, key, values)
                if key == "language_id":
                    key = "language"
                if key in [f.name for f in Supplier._meta.get_fields()]:
                    if key == "bank_currency" or key == "currency":
                        values = Currency.objects.get(id=values)
                    elif key == "gender":
                        values = Gender.objects.get(id=values)
                    elif key == "position":
                        values = Position.objects.get(id=values)
                    elif key == "company_number_of_employee":
                        values = NumberofEmployee.objects.get(id=values)
                    elif key == "company_country":
                        values = Country.objects.get(id=values)
                    elif key == "company_country_state":
                        values = CountryState.objects.get(id=values)
                    elif key == "language":
                        values = Language.objects.get(id=values)
                    elif key == "picture":
                        if values is None:
                            values = supplier.picture
                    elif key == "company_logo":
                        if values is None:
                            values = supplier.company_logo
                    elif key == "promotion":
                        values = Promotion.objects.get(id=values)
                    elif (
                            key == "profile_features"
                            and data.get('promotion') is not None
                            and Promotion.objects.get(id=data.get('promotion')).discount == 100
                    ):
                        values = ProfileFeaturesSupplier.objects.filter(id=values).first()
                        supplier.valid_from = timezone.now()
                        supplier.valid_to = timezone.now() + timezone.timedelta(days=365)
                        supplier.send_mail_30_day = None
                        supplier.send_mail_15_day = None
                        supplier.send_mail_7_day = None
                        supplier.send_mail_expire = None
                        profile_features = values
                    elif key == "profile_features":
                        values = supplier.profile_features
                    elif (
                            key == "sicp_registration"
                            and data.get('promotion') is not None
                            and Promotion.objects.get(id=data.get('promotion')).discount == 100
                    ):
                        values = SICPRegistration.objects.filter(id=values).first()
                        sicp_registration = values
                    elif key == "sicp_registration":
                        values = supplier.sicp_registration

                    setattr(supplier, key, values)

                if key == "company_credential_profiles" and values is not None:
                    SupplierCompanyCredential.objects.filter(supplier=supplier).delete()
                    for file in values:
                        SupplierCompanyCredential.objects.create(supplier=supplier, company_credential_profile=file)

                if key == 'form_registrations' and values is not None:
                    SupplierFormRegistrations.objects.filter(supplier=supplier).delete()
                    for file in values:
                        SupplierFormRegistrations.objects.create(supplier=supplier, form_registration=file)

                if key == 'bank_certifications' and values is not None:
                    SupplierBankCertification.objects.filter(supplier=supplier).delete()
                    for file in values:
                        SupplierBankCertification.objects.create(supplier=supplier, bank_certification=file)

                if key == 'quality_certifications' and values is not None:
                    SupplierQualityCertification.objects.filter(supplier=supplier).delete()
                    for file in values:
                        SupplierQualityCertification.objects.create(supplier=supplier, quality_certification=file)

                if key == 'business_licenses' and values is not None:
                    SupplierBusinessLicense.objects.filter(supplier=supplier).delete()
                    for file in values:
                        SupplierBusinessLicense.objects.create(supplier=supplier, business_license=file)

                if key == 'tax_certifications' and values is not None:
                    SupplierTaxCertification.objects.filter(supplier_id=supplier.id).delete()
                    for file in values:
                        SupplierTaxCertification.objects.create(supplier=supplier, tax_certification=file)
                if key == 'other' and values is not None:
                    SupplierOthers.objects.filter(supplier_id=supplier.id).delete()
                    for file in values:
                        SupplierOthers.objects.create(supplier=supplier, other=file)

                if key == 'core_business':
                    percentage_category = 0
                    for categories in values:
                        if len(categories) > 10:
                            error = Error(code="USER_11", message=UserError.USER_11)
                            raise GraphQLError("USER_11")
                        for category in categories:
                            percentage_category += category.percentage
                    if percentage_category != 100:
                        error = Error(code="USER_05", message=UserError.USER_05)
                        raise GraphQLError("USER_05")
                    for categories in values:
                        for category in categories:
                            category_mapping = SupplierCategory.objects.filter(
                                user_supplier=supplier, category_id=category.category
                            )
                            if category_mapping.exists():
                                category_mapping = category_mapping.first()
                                category_mapping.percentage = category.percentage
                                category_mapping.minimum_of_value = category.minimum_of_value
                                category_mapping.save()
                            else:
                                SupplierCategory.objects.create(
                                    percentage=category.percentage,
                                    minimum_of_value=category.minimum_of_value,
                                    user_supplier=supplier,
                                    category_id=category.category,
                                )
                    list_category_mapping = map(
                        lambda x: int(x.get('category_id')), SupplierCategory.objects.filter(user_supplier=supplier).values('category_id')
                    )
                    list_category_mapping = set(list_category_mapping)
                    list_category = []
                    for categories in values:
                        for category in categories:
                            list_category.append(int(category.category))
                    list_category = set(list_category)
                    list_delete = list_category_mapping.difference(list_category)
                    SupplierCategory.objects.filter(user_supplier=supplier, category_id__in=list_delete).delete()

                if key == 'industries':
                    if len(values) > 10:
                        error = Error(code="USER_04", message=UserError.USER_04)

                        raise GraphQLError("USER_04")

                    percentage_industry = 0
                    for industry in values:
                        percentage_industry += industry.percentage

                    if percentage_industry != 100:
                        error = Error(code="USER_06", message=UserError.USER_06)
                        raise GraphQLError("USER_06")

                    for industry in values:
                        industry_mapping = SupplierIndustry.objects.filter(
                            industry_sub_sectors_id=industry.industry_sub_sectors, user_supplier=supplier
                        )
                        if industry_mapping.exists():
                            industry_mapping = industry_mapping.first()
                            industry_mapping.percentage = industry.percentage
                            industry_mapping.save()
                        else:
                            SupplierIndustry.objects.create(
                                percentage=industry.percentage,
                                industry_sub_sectors_id=industry.industry_sub_sectors,
                                user_supplier=supplier,
                            )

                    #  delete industry
                    list_industry_mapping = map(
                        lambda x: x.get('industry_sub_sectors_id'),
                        SupplierIndustry.objects.filter(user_supplier=supplier).values('industry_sub_sectors_id'),
                    )
                    list_industry_mapping = set(list_industry_mapping)
                    list_industry = []
                    for industry in values:
                        list_industry.append(int(industry.industry_sub_sectors))
                    list_industry = set(list_industry)
                    list_delete = list_industry_mapping.difference(list_industry)
                    SupplierIndustry.objects.filter(user_supplier=supplier, industry_sub_sectors_id__in=list_delete).delete()

                if key == 'client_focus':
                    percentage_client_focus = 0
                    for client_focus in values:
                        percentage_client_focus += client_focus.percentage

                    if percentage_client_focus != 100:
                        error = Error(code="USER_06", message=UserError.USER_06)
                        raise GraphQLError("USER_06")

                    for client_focus in values:
                        client_focus_mapping = SupplierClientFocus.objects.filter(
                            client_focus_id=client_focus.client_focus, user_supplier=supplier
                        )
                        if client_focus_mapping.exists():
                            client_focus_mapping = client_focus_mapping.first()
                            client_focus_mapping.percentage = client_focus.percentage
                            client_focus_mapping.save()
                        else:
                            SupplierClientFocus.objects.create(
                                percentage=client_focus.percentage,
                                client_focus_id=client_focus.client_focus,
                                user_supplier=supplier,
                            )

                    #  delete client focus
                    list_client_focus_mapping = map(
                        lambda x: x.get('client_focus_id'),
                        SupplierClientFocus.objects.filter(user_supplier=supplier).values('client_focus_id'),
                    )
                    list_client_focus_mapping = set(list_client_focus_mapping)
                    list_client_focus = []
                    for client_focus in values:
                        list_client_focus.append(int(client_focus.client_focus))
                    list_client_focus = set(list_client_focus)
                    list_delete = list_client_focus_mapping.difference(list_client_focus)
                    SupplierClientFocus.objects.filter(user_supplier=supplier, client_focus_id__in=list_delete).delete()

                # portfolio
                if key == 'portfolios_delete':
                    for portfolio_delete in values:
                        SupplierPortfolio.objects.get(id=portfolio_delete).delete()
                if key == 'portfolios':
                    for portfolio in values:
                        if portfolio.id is not None:
                            supplier_portfolio = SupplierPortfolio.objects.get(id=portfolio.id)
                            for key, value in portfolio.items():
                                if key in [f.name for f in SupplierPortfolio._meta.get_fields()]:
                                    if key != "id":
                                        if key == 'image' and value is None:
                                            pass
                                        else:
                                            setattr(supplier_portfolio, key, value)
                            supplier_portfolio.save()
                        else:
                            SupplierPortfolio.objects.create(
                                company=portfolio.company,
                                project_name=portfolio.project_name,
                                value=portfolio.value,
                                project_description=portfolio.project_description,
                                image=portfolio.image,
                                user_supplier=supplier,
                            )

                if key == 'certificate_list':
                    valid_input = [x for x in values if x]
                    for file in valid_input:
                        file_type = None
                        if is_pdf(file):
                            file_type = SupplierCertificateType.PDF
                        if not file_type and file.name.split(".")[-1] == "csv":
                            file_type = SupplierCertificateType.CSV
                        if not file_type:
                            kind = filetype.guess(file)
                            if kind:
                                file_kind = kind.mime.split("/")[0]
                                if file_kind == "image":
                                    file_type = SupplierCertificateType.IMAGE
                                if file_kind == "video":
                                    file_type = SupplierCertificateType.VIDEO
                                if kind.extension in ["doc", "docx", "odt", "xls", "xlsx", "ods", "ppt", "pptx", "odp"]:
                                    file_type = SupplierCertificateType.DOC
                        if not file_type:
                            file_type = SupplierCertificateType.OTHER
                        SupplierCertificate.objects.create(
                            user_supplier=supplier,
                            file=file,
                            name="".join(file.name.split(".")[:-1]),
                            size=convert_size(file.size),
                            type=file_type
                        )
                if key == "certificate_remove":
                    valid_input = [x for x in values if x]
                    SupplierCertificate.objects.filter(user_supplier=supplier, id__in=valid_input).delete()

                if key == "company_tax" and values is not None:
                    if Supplier.objects.filter(company_tax=values).exclude(id=supplier.id).exists():
                        error = Error(code="USER_33", message=UserError.USER_33)
                        raise GraphQLError('USER_33')
                if key == "email" and values is not None:
                    if (User.objects.filter(email=values).exclude(id=user.id)).exists():
                        error = Error(code="USER_01", message=UserError.USER_01)
                        raise GraphQLError('USER_01')
                    else:
                        user.email = values
            supplier.save()
            user.save()
            if profile_features is not None:
                send_mail_upgraded(user, profile_features)
            if sicp_registration is not None:
                send_mail_sicp(user, sicp_registration)

            return SupplierDetailUpdate(status=True, supplier=supplier)
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return SupplierDetailUpdate(error=error, status=False)


class SupplierSubAccountInput(graphene.InputObjectType):
    gender = graphene.String(required=True)
    phone = graphene.String(required=True)
    language = graphene.String(required=True)
    position = graphene.String(required=True)
    picture = Upload()
    currency = graphene.String(required=True)
    user = graphene.Field(UserBasicInput, required=True)


class SupplierSubAccountCreate(graphene.Mutation):
    class Arguments:
        supplier_sub_account = SupplierSubAccountInput(required=True)

    error = graphene.Field(Error)
    status = graphene.Boolean()
    supplier_sub_account = graphene.Field(SupplierSubAccountNode)

    def mutate(self, info, supplier_sub_account):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
            supplier = user.supplier
            number_supplier_sub_account = supplier.profile_features.sub_user_accounts
            list_id = []
            list_sub_account = SupplierSubAccount.objects.filter(supplier=supplier)
            for ob in list_sub_account:
                list_id.append(ob.supplier_id)

            count = len(list_id)
            if count < number_supplier_sub_account:
                if user.isSupplier() and user.company_position == 1:
                    if (User.objects.filter(user_type=3, email=supplier_sub_account.user.email)).exists():
                        error = Error(code="USER_01", message=UserError.USER_01)
                        raise GraphQLError('USER_01')

                    user_count = SupplierSubAccount.objects.filter(supplier=supplier).count() + 1
                    username_sub_accounts = str(user.username)
                    username = username_sub_accounts + str("." + str(user_count)).zfill(1)
                    language = supplier_sub_account.language
                    user_supplier = User(username=username, user_type=3, company_position=2, language_id=language, **supplier_sub_account.user)
                    user_supplier.set_password(supplier_sub_account.user.password)
                    user_supplier.save()
                    gender = supplier_sub_account.gender
                    position = supplier_sub_account.position
                    currency = supplier_sub_account.currency

                    supplier_sub_account = SupplierSubAccount.objects.create(
                        gender_id=gender,
                        phone=supplier_sub_account.phone,
                        language_id=language,
                        position_id=position,
                        picture=supplier_sub_account.picture,
                        currency_id=currency,
                        user=user_supplier,
                        supplier=user.supplier,
                    )
                    return SupplierSubAccountCreate(status=True, supplier_sub_account=supplier_sub_account)
                else:
                    error = Error(code="USER_02", message=UserError.USER_01)
                    raise GraphQLError("USER_02")
            else:
                error = Error(code="USER_09", message=UserError.USER_09)
                raise GraphQLError("USER_09")
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return SupplierSubAccountCreate(status=False, error=error)


class SupplierSubAccountUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Meta:
        model = SupplierSubAccount
        exclude_fields = ['user', 'picture', 'supplier']
        allow_unauthenticated = True

    class Input:
        full_name = graphene.String()
        email = graphene.String()
        picture = Upload()
        password = graphene.String()

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
            if user.isSupplier() and user.company_position == 1:
                supplier_sub_account = SupplierSubAccount.objects.get(id=data.get('id'))
                if (User.objects.filter(user_type=3, email=data.get("email")).exclude(id=supplier_sub_account.user.id)).exists():
                    error = Error(code="USER_01", message=UserError.USER_01)
                    raise GraphQLError('USER_01')
                data.pop('id')
                user_sub = supplier_sub_account.user
                for key, value in data.items():
                    if key in [f.name for f in User._meta.get_fields()]:
                        if key == "language":
                            key = "language_id"
                            value = Language.objects.get(id=value)
                            value = value.id
                        setattr(user_sub, key, value)
                    if key == "language_id":
                        key = "language"
                    if key == "password":
                        user_sub.set_password(value)
                    if key in [f.name for f in BuyerSubAccounts._meta.get_fields()]:
                        if key == "currency":
                            value = Currency.objects.get(id=value)
                        elif key == "gender":
                            value = Gender.objects.get(id=value)
                        elif key == "position":
                            value = Position.objects.get(id=value)
                        elif key == "language":
                            value = Language.objects.get(id=value)
                        setattr(supplier_sub_account, key, value)
                user_sub.save()
                supplier_sub_account.save()
                return SupplierSubAccountUpdate(status=True, supplierSubAccount=supplier_sub_account)
            else:
                error = Error(code="USER_10", message=UserError.USER_10)
                raise GraphQLError("USER_10")
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return SupplierSubAccountUpdate(error=error, status=False)


class SupplierSubAccountsProfileUpdate(ModelUpdateMutation):
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Meta:
        model = SupplierSubAccount
        exclude_fields = ['id', 'user', 'picture', 'buyer']
        allow_unauthenticated = True

    class Input:
        full_name = graphene.String()
        picture = Upload()

    @classmethod
    def perform_mutation(cls, root, info, **data):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
            if not user.isSupplier() or user.company_position != 2:
                error = Error(code="USER_13", message=UserError.USER_13)
                raise GraphQLError("You must be supplier sub account")
            supplier_sub_account = SupplierSubAccount.objects.get(user=user)
            for key, values in data.items():
                if key in [f.name for f in User._meta.get_fields()]:
                    if key == "language":
                        key = "language_id"
                        values = Language.objects.get(id=values)
                        values = values.id
                    setattr(user, key, values)
                if key == "language_id":
                    key = "language"
                if key in [f.name for f in SupplierSubAccount._meta.get_fields()]:
                    if key == "currency":
                        values = Currency.objects.get(id=values)
                    elif key == "gender":
                        values = Gender.objects.get(id=values)
                    elif key == "position":
                        values = Position.objects.get(id=values)
                    elif key == "language":
                        values = Language.objects.get(id=values)
                    setattr(supplier_sub_account, key, values)
            user.save()
            supplier_sub_account.save()
            return SupplierSubAccountsProfileUpdate(status=True, supplierSubAccount=supplier_sub_account)
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return SupplierSubAccountsProfileUpdate(error=error, status=False)


class SupplierSubAccountStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_id = graphene.List(graphene.String, required=True)
        status = graphene.Int(required=True)
        reason_manual = graphene.String()

    def mutate(root, info, list_id, status, reason_manual=None):
        try:
            error = None
            try:
                token = GetToken.getToken(info)
            except:
                error = Error(code="USER_12", message=UserError.USER_12)

            if token.user.isAdmin():
                for id in list_id:
                    supplier_sub_account = SupplierSubAccount.objects.select_related('user').get(pk=id)
                    supplier_sub_account.user.status = status
                    supplier_sub_account_activity = SupplierSubAccountActivity.objects.create(
                        supplier_sub_account=supplier_sub_account,
                        changed_by_id=token.user.id,
                        reason_manual=reason_manual,
                        changed_state=status,
                    )
                    supplier_sub_account.user.save()
                return SupplierSubAccountStatusUpdate(status=True)
            else:
                error = Error(code="USER_02", message=UserError.USER_02)
                raise GraphQLError('USER_02')
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return SupplierSubAccountStatusUpdate(error=error, status=False)


# --------------------------- User Diamond Sponsor -----------------------------
class UserDiamondSponsorInput(graphene.InputObjectType):
    image = Upload(required=True)
    description = graphene.String()
    user_id = graphene.String(required=True)
    valid_from = graphene.DateTime(required=True)
    valid_to = graphene.DateTime(required=True)
    is_active = graphene.Boolean(required=True)
    is_confirmed = graphene.Int()
    text_editer = graphene.String()
    icon = Upload()
    product_name = graphene.String()


class UserDiamondSponsorCreate(graphene.Mutation):
    class Arguments:
        input = UserDiamondSponsorInput(required=True)

    status = graphene.Boolean()
    user_diamond_sponsor = graphene.Field(UserDiamondSponsorNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        if input.valid_from >= input.valid_to:
            error = Error(code="USER_07", message=UserError.USER_07)
            return UserDiamondSponsorCreate(status=False, error=error)

        if (input.valid_to - input.valid_from).days < 30 or (input.valid_to - input.valid_from).days > 30:
            error = Error(code="USER_07", message=UserError.USER_07)
            return UserDiamondSponsorCreate(status=False, error=error)

        input["user"] = User.objects.get(id=input.user_id)
        if input.valid_to < timezone.now():
            input["status"] = 2
            input["is_confirmed"] = 2
        else:
            input["status"] = 1
            input["is_confirmed"] = 2
        user_diamond_sponsor = UserDiamondSponsor.objects.create(**input)
        return UserDiamondSponsorCreate(status=True, user_diamond_sponsor=user_diamond_sponsor)


class UserDiamondSponsorTextEditer(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        text_editer = graphene.String(required=True)

    def mutate(root, info, text_editer):
        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_02", message=UserError.USER_02)
            return UserDiamondSponsorTextEditer(error=error, status=False)

        if token.user.isAdmin():
            diamond_sponsor_ids = map(
                lambda x: x.get('id'), UserDiamondSponsor.objects.all().values('id')
            )
            for i in diamond_sponsor_ids:
                user_diamond_sponsor = UserDiamondSponsor.objects.filter(id=i).first()
                user_diamond_sponsor.text_editer = text_editer
                user_diamond_sponsor.save()
            return UserDiamondSponsorTextEditer(status=True)
        else:
            error = Error(code="USER_12", message=UserError.USER_12)
            return UserDiamondSponsorTextEditer(error=error, status=False)


class UserDiamondSponsorUpdateStatusInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    is_active = graphene.Boolean(required=True)


class UserDiamondSponsorUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(UserDiamondSponsorUpdateStatusInput, required=True)

    def mutate(root, info, list_status):
        for i in list_status:
            user_diamond_sponsor = UserDiamondSponsor.objects.filter(id=i.id).first()
            user_diamond_sponsor.is_active = i.is_active
            user_diamond_sponsor.is_confirmed = 2
            user_diamond_sponsor.save()
        return UserDiamondSponsorUpdateStatus(status=True)


class UserDiamondSponsorIsConfirmedUpdateInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    is_confirmed = graphene.Int(required=True)


class UserDiamondSponsorIsConfirmedUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_is_confirmed = graphene.List(UserDiamondSponsorIsConfirmedUpdateInput, required=True)

    def mutate(root, info, list_is_confirmed):

        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_02", message=UserError.USER_02)
            return UserDiamondSponsorIsConfirmedUpdate(error=error, status=False)

        if token.user.isAdmin():
            for i in list_is_confirmed:
                user_diamond_sponsor = UserDiamondSponsor.objects.filter(id=i.id).first()
                user_diamond_sponsor.is_confirmed = i.is_confirmed
                user_diamond_sponsor.save()
            return UserDiamondSponsorIsConfirmedUpdate(status=True)
        else:
            error = Error(code="USER_12", message=UserError.USER_12)
            return UserDiamondSponsorIsConfirmedUpdate(error=error, status=False)


class UserDiamondSponsorUpdateInput(graphene.InputObjectType):
    image = Upload()
    description = graphene.String()
    is_active = graphene.Boolean()
    is_confirmed = graphene.Int()
    valid_from = graphene.types.datetime.DateTime()
    valid_to = graphene.types.datetime.DateTime()
    text_editer = graphene.String()
    icon = Upload()
    product_name = graphene.String()


class UserDiamondSponsorUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = UserDiamondSponsorUpdateInput(required=True)

    status = graphene.Boolean()
    user_diamond_sponsor = graphene.Field(UserDiamondSponsorNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user_diamond_sponsor = UserDiamondSponsor.objects.get(id=id)
            if token.user.isAdmin():
                user_diamond_sponsor.is_confirmed = input.is_confirmed
                user_diamond_sponsor.save()
                return UserDiamondSponsorUpdate(status=True, user_diamond_sponsor=user_diamond_sponsor)
            elif token.user.isSupplier():
                if user_diamond_sponsor.user_id == token.user_id:
                    for key, values in input.items():
                        if key in [f.name for f in UserDiamondSponsor._meta.get_fields()]:
                            setattr(user_diamond_sponsor, key, values)
                    user_diamond_sponsor.is_confirmed = 2
                    user_diamond_sponsor.save()
                    return UserDiamondSponsorUpdate(status=True, user_diamond_sponsor=user_diamond_sponsor)
        except Exception as e:
            raise Exception('you must be logged in')


class UserDiamondSponsorDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id):
        user_diamond_sponsor = UserDiamondSponsor.objects.get(pk=id).delete()
        return UserDiamondSponsorDelete(status=True)


# ----------------------------------------------------SICP-----------------------------------------------------------------

class SICPInput(graphene.InputObjectType):
    legal_status = graphene.List(Upload, null=True)
    bank_account = graphene.List(Upload, null=True)
    certification_management = graphene.List(Upload, null=True)
    due_diligence = graphene.List(Upload, null=True)
    financial_risk_management = graphene.List(Upload, null=True)
    supplier_id = graphene.String()
    sanction_check = graphene.String(null=True)


class SICPCreate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    sicp = graphene.Field(SupplierSICPNode)

    class Arguments:
        input = SICPInput(required=True)

    def mutate(root, info, input):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            if user.isAdmin():
                user_supplier_id = input.supplier_id
            elif user.isSupplier():
                user_supplier_id = user.get_profile().id
        except Exception as e:
            raise Exception('you must log in')

        sicp_registration = SICPRegistration.objects.filter(supplier__id=user_supplier_id).first()
        if sicp_registration.sicp_type == 1:
            error = Error(code="USER_16", message=UserError.USER_16)
            return SICPCreate(status=False, error=error)
        else:
            if input.legal_status is not None and len(input.legal_status) > 0:
                if sicp_registration.sicp_type == 2 or sicp_registration.sicp_type == 3 or sicp_registration.sicp_type == 4:
                    sicp_instance = SupplierSICP(
                        sanction_check=input.sanction_check,
                        is_confirmed=2,
                        is_reviewed=2,
                        created_date=timezone.now(),
                        supplier_id=user_supplier_id,
                    )
                    sicp_instance.save()

                    legal = SupplierSICPFile.objects.filter(sicp_type=5, sicp__supplier_id=user_supplier_id).order_by("-ordered").first()
                    if legal is None:
                        count = 0
                    else:
                        count = legal.ordered
                    ordered = count + 1
                    for i in input.legal_status:
                        sicp_hold_file = SupplierSICPFile(
                            file_name=i,
                            sicp_type=5,
                            ordered=ordered,
                            sicp_id=sicp_instance.id,
                            user_or_admin=1,
                        )
                        sicp_hold_file.save()
                    return SICPCreate(status=True, sicp=sicp_instance)
                else:
                    error = Error(code="USER_16", message=UserError.USER_16)
                    return SICPCreate(status=False, error=error)

            if input.bank_account is not None and len(input.bank_account) > 0:
                if sicp_registration.sicp_type == 2 or sicp_registration.sicp_type == 3 or sicp_registration.sicp_type == 4:
                    sicp_instance = SupplierSICP(
                        sanction_check=input.sanction_check,
                        is_confirmed=2,
                        is_reviewed=2,
                        created_date=timezone.now(),
                        supplier_id=user_supplier_id,
                    )
                    sicp_instance.save()

                    bank = SupplierSICPFile.objects.filter(sicp_type=1, sicp__supplier_id=user_supplier_id).order_by("-ordered").first()
                    if bank is None:
                        count = 0
                    else:
                        count = bank.ordered
                    ordered = count + 1
                    for i in input.bank_account:
                        sicp_hold_file = SupplierSICPFile(
                            file_name=i,
                            sicp_type=1,
                            ordered=ordered,
                            sicp_id=sicp_instance.id,
                            user_or_admin=1,
                        )
                        sicp_hold_file.save()
                    return SICPCreate(status=True, sicp=sicp_instance)
                else:
                    error = Error(code="USER_16", message=UserError.USER_16)
                    return SICPCreate(status=False, error=error)

            if input.certification_management is not None and len(input.certification_management) > 0:
                if sicp_registration.sicp_type == 3 or sicp_registration.sicp_type == 4:
                    sicp_instance = SupplierSICP(
                        sanction_check=input.sanction_check,
                        is_confirmed=2,
                        is_reviewed=2,
                        created_date=timezone.now(),
                        supplier_id=user_supplier_id,
                    )
                    sicp_instance.save()

                    certification = SupplierSICPFile.objects.filter(sicp_type=2, sicp__supplier_id=user_supplier_id).order_by("-ordered").first()
                    if certification is None:
                        count = 0
                    else:
                        count = certification.ordered
                    ordered = count + 1
                    for i in input.certification_management:
                        sicp_hold_file = SupplierSICPFile(
                            file_name=i,
                            sicp_type=2,
                            ordered=ordered,
                            sicp_id=sicp_instance.id,
                            user_or_admin=1,
                        )
                        sicp_hold_file.save()
                    return SICPCreate(status=True, sicp=sicp_instance)
                else:
                    error = Error(code="USER_16", message=UserError.USER_16)
                    return SICPCreate(status=False, error=error)

            if input.due_diligence is not None and len(input.due_diligence) > 0:
                if sicp_registration.sicp_type == 4:
                    sicp_instance = SupplierSICP(
                        sanction_check=input.sanction_check,
                        is_confirmed=2,
                        is_reviewed=2,
                        created_date=timezone.now(),
                        supplier_id=user_supplier_id,
                    )
                    sicp_instance.save()

                    due = SupplierSICPFile.objects.filter(sicp_type=3, sicp__supplier_id=user_supplier_id).order_by("-ordered").first()
                    if due is None:
                        count = 0
                    else:
                        count = due.ordered
                    ordered = count + 1
                    for i in input.due_diligence:
                        sicp_hold_file = SupplierSICPFile(
                            file_name=i,
                            sicp_type=3,
                            ordered=ordered,
                            sicp_id=sicp_instance.id,
                            user_or_admin=1,
                        )
                        sicp_hold_file.save()
                    return SICPCreate(status=True, sicp=sicp_instance)
                else:
                    error = Error(code="USER_16", message=UserError.USER_16)
                    return SICPCreate(status=False, error=error)

            if input.financial_risk_management is not None and len(input.financial_risk_management) > 0:
                if sicp_registration.sicp_type == 4:
                    sicp_instance = SupplierSICP(
                        sanction_check=input.sanction_check,
                        is_confirmed=2,
                        is_reviewed=2,
                        created_date=timezone.now(),
                        supplier_id=user_supplier_id,
                    )
                    sicp_instance.save()

                    financial = SupplierSICPFile.objects.filter(sicp_type=4, sicp__supplier_id=user_supplier_id).order_by("-ordered").first()
                    if financial is None:
                        count = 0
                    else:
                        count = financial.ordered
                    ordered = count + 1
                    for i in input.financial_risk_management:
                        sicp_hold_file = SupplierSICPFile(
                            file_name=i,
                            sicp_type=4,
                            ordered=ordered,
                            sicp_id=sicp_instance.id,
                            user_or_admin=1,
                        )
                        sicp_hold_file.save()
                    return SICPCreate(status=True, sicp=sicp_instance)
                else:
                    error = Error(code="USER_16", message=UserError.USER_16)
                    return SICPCreate(status=False, error=error)


class SupplierSICPUpdateInput(graphene.InputObjectType):
    id = graphene.Int(required=True)
    is_confirmed = graphene.Int()
    document_internal = graphene.List(Upload, null=True)
    document_external = graphene.List(Upload, null=True)
    is_internal_deleted = graphene.Boolean()
    is_external_deleted = graphene.Boolean()


class SupplierSICPUpdate(graphene.Mutation):
    status = graphene.Boolean()
    supplier_sicp = graphene.Field(SupplierSICPNode)
    error = graphene.Field(Error)

    class Arguments:
        input = SupplierSICPUpdateInput(required=True)

    def mutate(root, info, input):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            if token.user.isAdmin():
                sicp_instance = SupplierSICP.objects.filter(id=input.id).first()
                if input.is_confirmed == 1 or input.is_confirmed == 3:
                    sicp_instance.is_reviewed = 1
                if input.is_confirmed == 1 and sicp_instance.expired_date is None:
                    sicp_instance.expired_date = datetime.datetime.now() + datetime.timedelta(days=365)
                for key, values in input.items():
                    if key in [f.name for f in SupplierSICP._meta.get_fields()]:
                        setattr(sicp_instance, key, values)
                sicp_instance.save()

                if input.is_internal_deleted == True:
                    sicp_files = SupplierSICPFile.objects.filter(sicp_id=input.id, sicp_type=6)
                    if sicp_files is not None:
                        for i in sicp_files:
                            i.delete()

                if input.is_external_deleted == True:
                    sicp_files = SupplierSICPFile.objects.filter(sicp_id=input.id, sicp_type=7)
                    if sicp_files is not None:
                        for i in sicp_files:
                            i.delete()

                if input.document_internal is not None and len(input.document_internal) > 0:
                    internal = SupplierSICPFile.objects.filter(sicp_type=6, sicp_id=input.id).order_by("-ordered").first()
                    if internal is None:
                        count = 0
                    else:
                        count = internal.ordered
                    ordered = count + 1
                    for i in input.document_internal:
                        sicp_hold_file = SupplierSICPFile(
                            file_name=i,
                            sicp_type=6,
                            ordered=ordered,
                            sicp_id=input.id,
                            user_or_admin=2,
                        )
                        sicp_hold_file.save()

                if input.document_external is not None and len(input.document_external) > 0:
                    external = SupplierSICPFile.objects.filter(sicp_type=7, sicp_id=input.id).order_by("-ordered").first()
                    if external is None:
                        count = 0
                    else:
                        count = external.ordered
                    ordered = count + 1
                    for i in input.document_external:
                        sicp_hold_file = SupplierSICPFile(
                            file_name=i,
                            sicp_type=7,
                            ordered=ordered,
                            sicp_id=input.id,
                            user_or_admin=3,
                        )
                        sicp_hold_file.save()

                return SupplierSICPUpdate(status=True, supplier_sicp=sicp_instance)
            else:
                error = Error(code="USER_12", message=UserError.USER_12)
                return SupplierSICPUpdate(error=error, status=False)
        except:
            raise Exception('you must log in')


class SICPTextEditorCreateInput(graphene.InputObjectType):
    sicp_type = graphene.Int(required=True)
    text_editer_en = graphene.String()
    text_editer_vi = graphene.String()
    file_name_en = graphene.List(Upload)
    file_name_vi = graphene.List(Upload)
    is_file_en_deleted = graphene.Boolean()
    is_file_vi_deleted = graphene.Boolean()


class SICPTextEditorCreate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    sicp_text_editor = graphene.Field(SICPTextEditorNode)

    class Arguments:
        input = SICPTextEditorCreateInput(required=True)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_02", message=UserError.USER_02)
            return SICPTextEditorCreate(error=error, status=False)

        if token.user.isAdmin():
            if input.text_editer_en is None and input.text_editer_vi is None and input.file_name_en is None and input.file_name_vi is None:
                error = Error(code="USER_17", message=UserError.USER_17)
                return SICPTextEditorCreate(error=error, status=False)

            td = SICPTextEditor.objects.filter(sicp_type=input.sicp_type).first()
            files_en = SICPTextEditorFile.objects.filter(sicp_text_editor=td, file_version=1)
            files_vi = SICPTextEditorFile.objects.filter(sicp_text_editor=td, file_version=2)
            if td is not None:
                td.text_editer_en = input.text_editer_en
                td.text_editer_vi = input.text_editer_vi
                td.sicp_type = input.sicp_type
                td.save()

                if input.is_file_en_deleted:
                    if files_en is not None:
                        for i in files_en:
                            i.delete()
                if input.file_name_en is not None and len(input.file_name_en) > 0:
                    for i in input.file_name_en:
                        text_editor_file_instance = SICPTextEditorFile(
                            sicp_text_editor_id=td.id,
                            file_name=i,
                            file_version=1,
                        )
                        text_editor_file_instance.save()

                if input.is_file_vi_deleted:
                    if files_vi is not None:
                        for i in files_vi:
                            i.delete()
                if input.file_name_vi is not None and len(input.file_name_vi) > 0:
                    for i in input.file_name_vi:
                        text_editor_file_instance = SICPTextEditorFile(
                            sicp_text_editor_id=td.id,
                            file_name=i,
                            file_version=2,
                        )
                        text_editor_file_instance.save()

                return SICPTextEditorCreate(status=True, sicp_text_editor=td)
            else:
                sicp_text_editor_instance = SICPTextEditor(
                    text_editer_en=input.text_editer_en,
                    text_editer_vi=input.text_editer_vi,
                    sicp_type=input.sicp_type,
                )
                sicp_text_editor_instance.save()
                if input.file_name_en is not None and len(input.file_name_en) > 0:
                    for i in input.file_name_en:
                        text_editor_file_instance = SICPTextEditorFile(
                            sicp_text_editor_id=sicp_text_editor_instance.id,
                            file_name=i,
                            file_version=1,

                        )
                        text_editor_file_instance.save()
                if input.file_name_vi is not None and len(input.file_name_vi) > 0:
                    for i in input.file_name_vi:
                        text_editor_file_instance = SICPTextEditorFile(
                            sicp_text_editor_id=sicp_text_editor_instance.id,
                            file_name=i,
                            file_version=2,

                        )
                        text_editor_file_instance.save()
                return SICPTextEditorCreate(status=True, sicp_text_editor=sicp_text_editor_instance)
        else:
            error = Error(code="USER_12", message=UserError.USER_12)
            return SICPTextEditorCreate(error=error, status=False)


class SICPDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id):
        sicp_files = SupplierSICPFile.objects.filter(sicp_id=id)
        for i in sicp_files:
            i.delete()
        sicp = SupplierSICP.objects.get(pk=id).delete()
        return SICPDelete(status=True)


class UserDiamondSponsorFeeInput(graphene.InputObjectType):
    title = graphene.String()
    fee = graphene.Float()


class UserDiamondSponsorFeeCreate(graphene.Mutation):
    class Arguments:
        input = UserDiamondSponsorFeeInput(required=True)

    status = graphene.Boolean()
    user_diamond_sponsor_fee = graphene.Field(UserDiamondSponsorFeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        if "fee" in input and input.fee < 0:
            error = Error(code="USER_18", message=UserError.USER_18)
            return UserDiamondSponsorFeeCreate(status=False, error=error)

        user_diamond_sponsor_fee_instance = UserDiamondSponsorFee(title=input.title, fee=input.fee)
        user_diamond_sponsor_fee_instance.save()
        return UserDiamondSponsorFeeCreate(status=True, user_diamond_sponsor_fee=user_diamond_sponsor_fee_instance)


class UserDiamondSponsorFeeUpdate(graphene.Mutation):
    status = graphene.Boolean()
    user_diamond_sponsor_fee = graphene.Field(UserDiamondSponsorFeeNode)
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)
        input = UserDiamondSponsorFeeInput(required=True)

    def mutate(root, info, id, input):
        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
            user = token.user
            user_diamond_sponsor_fee = UserDiamondSponsorFee.objects.filter(id=id).first()
            if user.isAdmin():
                for key, values in input.items():
                    if key in [f.name for f in UserDiamondSponsorFee._meta.get_fields()]:
                        setattr(user_diamond_sponsor_fee, key, values)
                user_diamond_sponsor_fee.save()
                return UserDiamondSponsorFeeUpdate(status=True, user_diamond_sponsor_fee=user_diamond_sponsor_fee)
        except Exception as e:
            raise Exception('you must be logged in')


class UserDiamondSponsorFeeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id):
        user_diamond_sponsor_fee = UserDiamondSponsorFee.objects.get(pk=id).delete()
        return UserDiamondSponsorDelete(status=True)


class SupplierView(graphene.Mutation):
    status = graphene.Boolean()
    supplier = graphene.Field(SupplierNode)
    error = graphene.Field(Error)

    class Arguments:
        supplier_id = graphene.String(required=True)

    def mutate(root, info, supplier_id):
        supplier_instance = Supplier.objects.filter(id=supplier_id).first()
        supplier_instance.viewed += 1
        supplier_instance.save()
        return SupplierView(status=True, supplier=supplier_instance)


class SupplierFlashSaleClickCount(graphene.Mutation):
    status = graphene.Boolean()
    supplier_flash_sale = graphene.Field(SupplierFlashSaleNode)
    error = graphene.Field(Error)

    class Arguments:
        supplier_flash_sale_id = graphene.String(required=True)

    def mutate(root, info, supplier_flash_sale_id):
        try:
            key = info.context.headers.get('Authorization')
            if key:
                key = key.split(" ")[-1]
            token = Token.objects.get(key=key)
            user = token.user
            supplier_flash_sale = SupplierFlashSale.objects.filter(id=supplier_flash_sale_id).first()
            if supplier_flash_sale is None:
                return SupplierFlashSaleClickCount(status=False, error=Error(code="USER_14", message=UserError.USER_14))
            if user.isSupplier():
                if user.supplier_sub_account.exists():
                    if user.supplier_sub_account.first().supplier == supplier_flash_sale.user_supplier:
                        return SupplierFlashSaleClickCount(status=True, supplier_flash_sale=supplier_flash_sale)
                else:
                    if user.supplier == supplier_flash_sale.user_supplier:
                        return SupplierFlashSaleClickCount(status=True, supplier_flash_sale=supplier_flash_sale)
            supplier_flash_sale.click_number += 1
            supplier_flash_sale.save()
            return SupplierFlashSaleClickCount(status=True, supplier_flash_sale=supplier_flash_sale)
        except Exception as e:
            raise Exception('you must be logged in')


class SupplierProductClickCount(graphene.Mutation):
    status = graphene.Boolean()
    supplier_product = graphene.Field(SupplierProductNode)
    error = graphene.Field(Error)

    class Arguments:
        supplier_product_id = graphene.String(required=True)

    def mutate(root, info, supplier_product_id):
        try:
            supplier_product = SupplierProduct.objects.filter(id=supplier_product_id).first()
            if supplier_product is None:
                return SupplierProductClickCount(status=False, error=Error(code="USER_24", message=UserError.USER_24))
            key = info.context.headers.get('Authorization')
            if key:
                key = key.split(" ")[-1]
            token = Token.objects.filter(key=key).first()
            if token is not None:
                user = token.user
                if user.isSupplier():
                    if user.supplier_sub_account.exists():
                        if user.supplier_sub_account.first().supplier == supplier_product.user_supplier:
                            return SupplierProductClickCount(status=True, supplier_product=supplier_product)
                    else:
                        if user.supplier == supplier_product.user_supplier:
                            return SupplierProductClickCount(status=True, supplier_product=supplier_product)
            supplier_product.click_number += 1
            supplier_product.save()
            return SupplierProductClickCount(status=True, supplier_product=supplier_product)
        except Exception as e:
            return SupplierProductClickCount(status=False, error=e)


class UserDiamondSponsorClickCount(graphene.Mutation):
    status = graphene.Boolean()
    diamond_sponsor = graphene.Field(UserDiamondSponsorNode)
    error = graphene.Field(Error)

    class Arguments:
        diamond_sponsor_id = graphene.String(required=True)

    def mutate(root, info, diamond_sponsor_id):
        try:
            diamond_sponsor = UserDiamondSponsor.objects.filter(id=diamond_sponsor_id).first()
            if diamond_sponsor is None:
                return UserDiamondSponsorClickCount(status=False, error=Error(code="USER_31", message=UserError.USER_31))
            key = info.context.headers.get('Authorization')
            if key:
                key = key.split(" ")[-1]
            token = Token.objects.filter(key=key).first()
            if token is not None:
                user = token.user
                if user.isSupplier():
                    if user.supplier_sub_account.exists():
                        if user.supplier_sub_account.first().supplier == diamond_sponsor.user.supplier:
                            return UserDiamondSponsorClickCount(status=True, diamond_sponsor=diamond_sponsor)
                    else:
                        if user == diamond_sponsor.user:
                            return UserDiamondSponsorClickCount(status=True, diamond_sponsor=diamond_sponsor)
            diamond_sponsor.click_number += 1
            diamond_sponsor.save()
            return UserDiamondSponsorClickCount(status=True, diamond_sponsor=diamond_sponsor)
        except Exception as e:
            return UserDiamondSponsorClickCount(status=False, error=e)


class ProductTypeInput(graphene.Enum):
    PRODUCT = ProductType.PRODUCT
    FLASH_SALE = ProductType.FLASH_SALE


class ProductConfirmStatusInput(graphene.Enum):
    APPROVED = ProductConfirmStatus.APPROVED
    WAITING = ProductConfirmStatus.WAITING
    REJECTED = ProductConfirmStatus.REJECTED


class ProductCreateConfirmStatusInput(graphene.Enum):
    DRAFT = ProductConfirmStatus.DRAFT
    WAITING = ProductConfirmStatus.WAITING


class ProductInventoryStatusInput(graphene.Enum):
    STOCKING = ProductInventoryStatus.STOCKING
    OUT_OF_STOCK = ProductInventoryStatus.OUT_OF_STOCK


class ProductWholesalePriceInput(graphene.InputObjectType):
    quality_from = graphene.Float()
    quality_to = graphene.Float()
    price_bracket = graphene.Float()
    delivery_days = graphene.Int()


class SupplierProductCreateInput(graphene.InputObjectType):
    type = ProductTypeInput(required=True)
    product_name = graphene.String()
    unit_of_measure = graphene.String()
    sku_number = graphene.String()
    is_visibility = graphene.Boolean()
    description = graphene.String()
    specification = graphene.String()
    minimum_order_quantity = graphene.String()
    initial_price = graphene.Float()
    discounted_price = graphene.Float()
    wholesale_price_list = graphene.List(ProductWholesalePriceInput)
    related_product_list = graphene.List(graphene.String)
    payment_term = graphene.String()
    provide_ability = graphene.String()
    support = graphene.String()
    brand = graphene.String()
    other_information = graphene.String()
    origin_of_production = graphene.String()
    guarantee = graphene.String()
    inventory_status = ProductInventoryStatusInput()
    user_supplier_id = graphene.String()
    image_list = graphene.List(Upload)
    category_list = graphene.List(graphene.String)
    confirmed_status = ProductCreateConfirmStatusInput()
    origin_of_production_country = graphene.String()
    weight = graphene.Float()
    create_date = graphene.Date()
    color = graphene.String()
    size = graphene.String()
    height = graphene.Float()   
    format = graphene.String()  


class SupplierProductCreate(graphene.Mutation):
    class Arguments:
        input = SupplierProductCreateInput(required=True)

    status = graphene.Boolean(default_value=False)
    supplier_product = graphene.Field(SupplierProductNode)
    error = graphene.Field(Error)

    @transaction.atomic
    def mutate(root, info, input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
                return SupplierProductCreate(status=False, error=error)
            if user.isAdmin():
                if not input.user_supplier_id or not Supplier.objects.filter(user_id=input.user_supplier_id).exists():
                    error = Error(code="USER_22", message=UserError.USER_22)
                    return SupplierProductCreate(status=False, error=error)
                user_supplier = Supplier.objects.filter(user_id=input.user_supplier_id).first()
            elif user.isSupplier():
                user_supplier = user.get_profile()
            else:
                error = Error(code="USER_02", message=UserError.USER_02)
                return SupplierProductCreate(status=False, error=error)

            if input.get("unit_of_measure"):
                if not UnitofMeasure.objects.filter(id=input.unit_of_measure).exists():
                    error = Error(code="USER_21", message=UserError.USER_21)
                    return SupplierProductCreate(status=False, error=error)
                input["unit_of_measure"] = UnitofMeasure.objects.filter(id=input.get("unit_of_measure")).first()

            if input.get("sku_number"):
                if SupplierProduct.objects.filter(
                        sku_number=input.sku_number,
                        user_supplier=user_supplier
                ).exists():
                    return SupplierProductCreate(
                        error=Error(
                            code="USER_20",
                            message=UserError.USER_20
                        )
                    )

            if input.get("initial_price", False) and input.get("discounted_price", False) and input.initial_price <= input.discounted_price:
                error = Error(code="USER_23", message=UserError.USER_23)
                return SupplierProductCreate(status=False, error=error)

            if user.isSupplier():
                if input.type == ProductType.FLASH_SALE:
                    flash_sale_active_count = user_supplier.supplier_products.filter(
                        type=ProductType.FLASH_SALE
                    ).count()

                    if user_supplier.profile_features.flash_sale <= flash_sale_active_count:
                        error = Error(code="USER_19", message=UserError.USER_19)
                        return SupplierProductCreate(status=False, error=error)
                else:
                    product_active_count = user_supplier.supplier_products.filter(
                        type=ProductType.PRODUCT
                    ).count()

                    if user_supplier.profile_features.product <= product_active_count:
                        error = Error(code="USER_25", message=UserError.USER_25)
                        return SupplierProductCreate(status=False, error=error)

            if input.get("related_product_list") \
                    and not all(SupplierProduct.objects.filter(id=x, user_supplier=user_supplier).exists() for x in input.get("related_product_list")):
                error = Error(code="USER_19", message=UserError.USER_19)
                return SupplierProductCreate(status=False, error=error)

            if input.get("payment_term"):
                if not PaymentTerm.objects.filter(id=input.get("payment_term")).exists():
                    error = Error(code="USER_28", message=UserError.USER_28)
                    return SupplierProductCreate(status=False, error=error)
                input["payment_term"] = PaymentTerm.objects.filter(id=input.get("payment_term")).first()

            if "category_list" in input:
                category_id_list = [x for x in input.get("category_list") if x]
                if not all(Category.objects.filter(id=x).exists() for x in category_id_list):
                    error = Error(code="USER_29", message=UserError.USER_29)
                    return SupplierProductCreate(status=False, error=error)

            if input.get("origin_of_production_country"):
                if not Country.objects.filter(id=input.get("origin_of_production_country")).exists():
                    return SupplierProductCreate(
                        status=False,
                        error=Error(code="USER_32", message=UserError.USER_32)
                    )
                input["origin_of_production_country"] = Country.objects.get(id=input.get("origin_of_production_country"))

            if not input.get("confirmed_status"):
                input.confirmed_status = ProductConfirmStatus.WAITING
                input.create_date = datetime.datetime.now().strftime("%Y-%m-%d")

            supplier_product = SupplierProduct(
                user_supplier=user_supplier
            )
            f_name = [f.name for f in SupplierProduct._meta.get_fields()]
            for key, value in input.items():
                if key in f_name and key not in ["wholesale_price", "origin_of_production"] and input.get(key) != None:
                    setattr(supplier_product, key, value)

            if supplier_product.origin_of_production_country:
                supplier_product.origin_of_production = supplier_product.origin_of_production_country.name
            supplier_product.save()

            if input.get("image_list"):
                for image in input.image_list:
                    if image:
                        SupplierProductImage.objects.create(supplier_product=supplier_product, image=image)
            SupplierProductFlashSale.objects.create(
                supplier_product=supplier_product,
                initial_price=input.get("initial_price"),
                discounted_price=input.get("discounted_price"),
            )
            if input.get("wholesale_price_list"):
                for wholesale_price in input.wholesale_price_list:
                    SupplierProductWholesalePrice.objects.create(
                        supplier_product=supplier_product,
                        quality_from=wholesale_price.get("quality_from"),
                        quality_to=wholesale_price.get("quality_to"),
                        price_bracket=wholesale_price.get("price_bracket"),
                        delivery_days=wholesale_price.get("delivery_days"),
                    )
            if input.get("related_product_list"):
                for supplier_product_id in input.get("related_product_list"):
                    RelatedSupplierProduct.objects.create(
                        supplier_product=supplier_product,
                        related_supplier_product_id=supplier_product_id
                    )
            if "category_list" in input:
                for x in input.get("category_list"):
                    if x:
                        SupplierProductCategory.objects.create(
                            supplier_product=supplier_product,
                            category_id=x
                        )
            return SupplierProductCreate(status=True, supplier_product=supplier_product)
        except Exception as error:
            transaction.set_rollback(True)
            return SupplierProductCreate(status=True, error=error)


class ProductWholesalePriceUpdateInput(graphene.InputObjectType):
    id = graphene.String()
    quality_from = graphene.Float()
    quality_to = graphene.Float()
    price_bracket = graphene.Float()
    delivery_days = graphene.Int()


class SupplierProductUpdateInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    product_name = graphene.String()
    unit_of_measure = graphene.String()
    sku_number = graphene.String()
    is_visibility = graphene.Boolean()
    description = graphene.String()
    specification = graphene.String()
    minimum_order_quantity = graphene.String()
    initial_price = graphene.Float()
    discounted_price = graphene.Float()
    wholesale_price_list = graphene.List(ProductWholesalePriceUpdateInput)
    related_product_list = graphene.List(graphene.String)
    payment_term = graphene.String()
    provide_ability = graphene.String()
    support = graphene.String()
    brand = graphene.String()
    other_information = graphene.String()
    origin_of_production_country = graphene.String()
    guarantee = graphene.String()
    confirmed_status = ProductConfirmStatusInput()
    image_list = graphene.List(Upload)
    image_remove_list = graphene.List(graphene.String)
    inventory_status = ProductInventoryStatusInput()
    category_list = graphene.List(graphene.String)
    weight = graphene.Float()
    color = graphene.String()
    size = graphene.String()
    height = graphene.Float()   
    format = graphene.String()  


class SupplierProductUpdate(graphene.Mutation):
    class Arguments:
        input = SupplierProductUpdateInput(required=True)

    status = graphene.Boolean()
    supplier_product = graphene.Field(SupplierProductNode)
    error = graphene.Field(Error)

    @transaction.atomic
    def mutate(root, info, input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
                return SupplierProductUpdate(status=False, error=error)

            if not (user.isAdmin() or user.isSupplier()):
                error = Error(code="USER_02", message=UserError.USER_02)
                return SupplierProductUpdate(status=False, error=error)

            if input.get("initial_price", False) and input.get("discounted_price", False) and input.initial_price <= input.discounted_price:
                error = Error(code="USER_23", message=UserError.USER_23)
                return SupplierProductUpdate(status=False, error=error)

            if user.isAdmin():
                supplier_product = SupplierProduct.objects.filter(id=input.id).first()
            else:
                supplier_product = SupplierProduct.objects.filter(id=input.id, user_supplier__user=user).first()
            if supplier_product is None:
                error = Error(code="USER_24", message=UserError.USER_24)
                return SupplierProductUpdate(status=False, error=error)

            user_supplier = supplier_product.user_supplier
            if input.get("sku_number") \
                    and SupplierProduct.objects.filter(
                sku_number=input.sku_number,
                user_supplier=user_supplier
            ).exclude(id=input.id).exists():
                return SupplierProductUpdate(
                    error=Error(
                        code="USER_20",
                        message=UserError.USER_20
                    )
                )

            if input.get("wholesale_price_list") is not None and \
                    not all(SupplierProductWholesalePrice.objects.filter(
                        supplier_product=supplier_product,
                        id=x.id
                    ).exists() for x in input.wholesale_price_list if x.id):
                return SupplierProductUpdate(status=False, error=Error(code="USER_26", message=UserError.USER_26))

            if input.get("related_product_list") is not None \
                    and not all(
                SupplierProduct.objects.filter(
                    id=x,
                    user_supplier=user_supplier
                ).exists() for x in input.related_product_list if x
            ):
                return SupplierProductUpdate(status=False, error=Error(code="USER_24", message=UserError.USER_24))

            if input.get("image_remove_list") and \
                    not all(SupplierProductImage.objects.filter(
                        id=x,
                        supplier_product=supplier_product
                    ).exists() for x in input.get("image_remove_list")):
                return SupplierProductUpdate(status=False, error=Error(code="USER_27", message=UserError.USER_27))

            if input.get("unit_of_measure"):
                if not UnitofMeasure.objects.filter(id=input.unit_of_measure).exists():
                    error = Error(code="USER_21", message=UserError.USER_21)
                    return SupplierProductUpdate(status=False, error=error)
                input["unit_of_measure"] = UnitofMeasure.objects.filter(id=input.get("unit_of_measure")).first()

            if "payment_term" in input:
                if input.get("payment_term"):
                    if not PaymentTerm.objects.filter(id=input.get("payment_term")).exists():
                        error = Error(code="USER_28", message=UserError.USER_28)
                        return SupplierProductUpdate(status=False, error=error)
                    input["payment_term"] = PaymentTerm.objects.filter(id=input.get("payment_term")).first()
                else:
                    input["payment_term"] = supplier_product.payment_term

            if "category_list" in input:
                category_id_list = [x for x in input.get("category_list") if x]
                if not all(Category.objects.filter(id=x).exists() for x in category_id_list):
                    error = Error(code="USER_29", message=UserError.USER_29)
                    return SupplierProductCreate(status=False, error=error)

            if input.get("origin_of_production_country"):
                if not Country.objects.filter(id=input.origin_of_production_country).exists():
                    error = Error(code="USER_32", message=UserError.USER_32)
                    return SupplierProductUpdate(status=False, error=error)
                input["origin_of_production_country"] = Country.objects.get(id=input.get("origin_of_production_country"))

            is_change = False
            if user.isAdmin():
                if input.get("confirmed_status"):
                    supplier_product.confirmed_status = input.confirmed_status

            elif user.isSupplier():
                for key, value in input.items():
                    if key in [f.name for f in SupplierProduct._meta.get_fields()]:
                        if not is_change and key not in ["is_visibility", "confirmed_status", "id"] and getattr(supplier_product, key) != value:
                            is_change = True
                            setattr(supplier_product, key, value)

            if supplier_product.origin_of_production_country:
                supplier_product.origin_of_production = supplier_product.origin_of_production_country.name
            else:
                supplier_product.origin_of_production = None
            if input.get("wholesale_price_list") is not None:
                wholesale_price_id_list = [x.id for x in input.wholesale_price_list if x.id]
                delete_value = SupplierProductWholesalePrice.objects.filter(supplier_product=supplier_product).exclude(id__in=wholesale_price_id_list).delete()
                if not is_change and delete_value[0] != 0:
                    is_change = True
                for wholesale_price in input.wholesale_price_list:
                    if wholesale_price.id:
                        product_wholesale_price = SupplierProductWholesalePrice.objects.get(id=wholesale_price.id)
                        if "quality_from" in wholesale_price:
                            if not is_change and product_wholesale_price.quality_from != wholesale_price.quality_from:
                                is_change = True
                            product_wholesale_price.quality_from = wholesale_price.quality_from
                        if "quality_to" in wholesale_price:
                            if not is_change and product_wholesale_price.quality_to != wholesale_price.quality_to:
                                is_change = True
                            product_wholesale_price.quality_to = wholesale_price.quality_to
                        if "price_bracket" in wholesale_price:
                            if not is_change and product_wholesale_price.price_bracket != wholesale_price.price_bracket:
                                is_change = True
                            product_wholesale_price.price_bracket = wholesale_price.price_bracket
                        if "delivery_days" in wholesale_price:
                            if not is_change and product_wholesale_price.delivery_days != wholesale_price.delivery_days:
                                is_change = True
                            product_wholesale_price.delivery_days = wholesale_price.delivery_days
                        product_wholesale_price.save()
                    else:
                        if wholesale_price.get("quality_from") or wholesale_price.get("quality_to") or wholesale_price.get("price_bracket") or wholesale_price.get("delivery_days"):
                            SupplierProductWholesalePrice.objects.create(
                                supplier_product=supplier_product,
                                quality_from=wholesale_price.get("quality_from"),
                                quality_to=wholesale_price.get("quality_to"),
                                price_bracket=wholesale_price.get("price_bracket"),
                                delivery_days=wholesale_price.get("delivery_days"),
                            )
                            if not is_change:
                                is_change = True

            if "related_product_list" in input:
                related_product_id_list = [x for x in input.related_product_list if x]
                delete_value = supplier_product.related_supplier_product_product.exclude(related_supplier_product_id__in=related_product_id_list).delete()
                if not is_change and delete_value[0] != 0:
                    is_change = True
                for x in related_product_id_list:
                    if not RelatedSupplierProduct.objects.filter(
                            supplier_product=supplier_product,
                            related_supplier_product_id=x
                    ).exists():
                        RelatedSupplierProduct.objects.create(
                            supplier_product=supplier_product,
                            related_supplier_product_id=x
                        )
                        if not is_change:
                            is_change = True

            if input.get("image_list"):
                for image in input.image_list:
                    if image:
                        SupplierProductImage.objects.create(supplier_product=supplier_product, image=image)
                        if not is_change:
                            is_change = True

            if input.get("image_remove_list"):
                SupplierProductImage.objects.filter(supplier_product=supplier_product, id__in=input.image_remove_list).delete()
                if not is_change:
                    is_change = True

            if "category_list" in input:
                category_id_list = [x for x in input.get("category_list") if x]
                SupplierProductCategory.objects.filter(supplier_product=supplier_product).exclude(category_id__in=category_id_list).delete()
                for category_id in category_id_list:
                    if not SupplierProductCategory.objects.filter(
                            supplier_product=supplier_product,
                            category_id=category_id
                    ).exists():
                        SupplierProductCategory.objects.create(
                            supplier_product=supplier_product,
                            category_id=category_id
                        )
            if user.isSupplier():
                if supplier_product.confirmed_status == ProductConfirmStatus.DRAFT:
                    if input.get("confirmed_status") and input.confirmed_status == ProductConfirmStatus.WAITING:
                        supplier_product.confirmed_status = input.confirmed_status
                        supplier_product.create_date = datetime.datetime.now().strftime("%Y-%m-%d")
                else:
                    if is_change:
                        supplier_product.confirmed_status = ProductConfirmStatus.WAITING

            supplier_product.save()
            return SupplierProductUpdate(status=True, supplier_product=supplier_product)
        except Exception as error:
            transaction.set_rollback(True)
            return SupplierProductUpdate(status=True, error=error)


class SupplierProductDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.ID(required=True)

    @transaction.atomic
    def mutate(root, info, **kwargs):
        try:
            supplier_product = SupplierProduct.objects.get(pk=kwargs["id"])
            supplier_product.delete()
            return SupplierProductDelete(status=True)
        except Exception as error:
            transaction.set_rollback(True)
            return SupplierProductDelete(status=False, error=error)


class SupplierProductUpdateStatusInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    is_visibility = graphene.Boolean(required=True)


class SupplierProductUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_status = graphene.List(SupplierProductUpdateStatusInput, required=True)

    @transaction.atomic
    def mutate(root, info, list_status):
        try:
            for i in list_status:
                supplier_product = SupplierProduct.objects.filter(id=i.id).first()
                if supplier_product.confirmed_status != ProductConfirmStatus.REJECTED:
                    if supplier_product.is_visibility == True and i.is_visibility == False:
                        supplier_product.confirmed_status = ProductConfirmStatus.APPROVED
                    else:
                        supplier_product.confirmed_status = ProductConfirmStatus.WAITING
                elif supplier_product.confirmed_status == ProductConfirmStatus.REJECTED \
                        and supplier_product.is_visibility == True \
                        and i.is_visibility == False:
                    supplier_product.confirmed_status = ProductConfirmStatus.APPROVED
                supplier_product.is_visibility = i.is_visibility
                supplier_product.save()

            return SupplierProductUpdateStatus(status=True)
        except Exception as error:
            transaction.set_rollback(True)
            return SupplierProductUpdateStatus(status=False, error=error)


class SupplierProductConfirmedStatusUpdateInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    confirmed_status = ProductConfirmStatusInput(required=True)


class SupplierProductConfirmedStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_is_confirmed = graphene.List(SupplierProductConfirmedStatusUpdateInput, required=True)

    @transaction.atomic
    def mutate(root, info, list_is_confirmed):

        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_02", message=UserError.USER_02)
            return SupplierProductConfirmedStatusUpdate(error=error, status=False)

        if not token.user.isAdmin():
            error = Error(code="USER_12", message=UserError.USER_12)
            return SupplierProductConfirmedStatusUpdate(error=error, status=False)

        for i in list_is_confirmed:
            supplier_product = SupplierProduct.objects.filter(id=i.id).first()
            supplier_product.confirmed_status = i.confirmed_status
            supplier_product.save()
        return SupplierProductConfirmedStatusUpdate(status=True)
class FollowStatus(graphene.Enum):
    FOLLOWING = UserFollowingSupplierStatus.FOLLOWING
    UN_FOLLOW = UserFollowingSupplierStatus.UN_FOLLOW
class UserFollowingSupplierInput(graphene.InputObjectType):
    supplier_id = graphene.String(required=True)
    user_id = graphene.String(required=True)
    follow_status = FollowStatus(required=True)
    
class UserFollowingSupplierCreate(graphene.Mutation):
    class Arguments:
        input = UserFollowingSupplierInput(required=True)

    status = graphene.Boolean()
    user_following_supplier = graphene.Field(UserFollowingSupplierNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        error = None
        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_02", message=UserError.USER_02)
            return UserFollowingSupplierUpdate(error=error, status=False)
        user_following_instance = UserFollowingSupplier(user_id=input.user_id,supplier_id=input.supplier_id,follow_status=input.follow_status)
        user_following_instance.save()
        return UserFollowingSupplierCreate(status=True, user_following_supplier=user_following_instance)
    
class UserFollowingSupplierUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)
        follow_status =  FollowStatus(required=True)

    def mutate(root, info, id, follow_status):
        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_12", message=UserError.USER_12)
            return UserFollowingSupplierUpdate(error=error, status=False)

        user_following_current = UserFollowingSupplier.objects.get(id=id)
        user_following_current.follow_status = follow_status
        user_following_current.save()
        return UserFollowingSupplierUpdate(status=True)

class UserRatingSupplierProductInput(graphene.InputObjectType):
    supplier_product_id = graphene.String(required=True)
    user_id = graphene.String(required=True)
    quality_rating = graphene.Int()
    delivery_time_rating = graphene.Int()

class UserRatingSupplierProductUpdate(graphene.Mutation):
    status = graphene.Boolean()
    user_rating_supplier_product = graphene.Field(UserRatingSupplierProductNode)
    error = graphene.Field(Error)

    class Arguments:
        input = UserRatingSupplierProductInput(required=True)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
        except:
            error = Error(code="USER_12", message=UserError.USER_12)
            return UserRatingSupplierProductUpdate(error=error, status=False)

        try:
            user_id = input.user_id
            supplier_product_id = input.supplier_product_id
            print('params: {}'.format(input))
            try:
                user_rating_supplier_product = UserRatingSupplierProduct.objects.get(user_id = user_id, supplier_product_id = supplier_product_id)
                print('user_rating_supplier_product update')
                if input.quality_rating is not None:
                    user_rating_supplier_product.quality_rating = input.quality_rating

                if input.delivery_time_rating is not None:
                    user_rating_supplier_product.delivery_time_rating = input.delivery_time_rating
                
                user_rating_supplier_product.save()
                return UserRatingSupplierProductUpdate(status=True, user_rating_supplier_product = user_rating_supplier_product)
            except UserRatingSupplierProduct.DoesNotExist:
                print('user_rating_supplier_product create')
                user_rating_supplier_product = UserRatingSupplierProduct(
                    user_id = input.user_id,
                    supplier_product_id = input.supplier_product_id
                )
                
                if input.quality_rating is not None:
                    user_rating_supplier_product.quality_rating = input.quality_rating

                if input.delivery_time_rating is not None:
                    user_rating_supplier_product.delivery_time_rating = input.delivery_time_rating

                user_rating_supplier_product.save()
                return UserRatingSupplierProductUpdate(status=True, user_rating_supplier_product = user_rating_supplier_product)
        except Exception as errors:
            transaction.set_rollback(True)
            if error is None:
                error = errors
            return UserRatingSupplierProductUpdate(error=error, status=False)

class Mutation(graphene.ObjectType):
    buyer_register = BuyerRegister.Field()
    buyer_detail_update = BuyerDetailUpdate.Field()

    buyer_sub_accounts_update = BuyerSubAccountsUpdate.Field()
    buyer_sub_accounts_profile_update = BuyerSubAccountsProfileUpdate.Field()

    supplier_register = SupplierRegister.Field()
    supplier_detail_update = SupplierDetailUpdate.Field()
    supplier_view = SupplierView.Field()

    supplier_sub_accounts_create = SupplierSubAccountCreate.Field()
    supplier_sub_accounts_update = SupplierSubAccountUpdate.Field()

    supplier_sub_accounts_profile_update = SupplierSubAccountsProfileUpdate.Field()
    supplier_sub_accounts_status_update = SupplierSubAccountStatusUpdate.Field()

    user_diamond_sponsor_create = UserDiamondSponsorCreate.Field()
    user_diamond_sponsor_update = UserDiamondSponsorUpdate.Field()
    user_diamond_sponsor_delete = UserDiamondSponsorDelete.Field()
    user_diamond_sponsor_status_update = UserDiamondSponsorUpdateStatus.Field()
    user_user_diamond_sponsor_is_confirmed_update = UserDiamondSponsorIsConfirmedUpdate.Field()
    user_diamond_sponsor_create_text_editer = UserDiamondSponsorTextEditer.Field()
    user_diamond_sponsor_click_count = UserDiamondSponsorClickCount.Field()

    user_supplier_sicp_create = SICPCreate.Field()
    user_supplier_sicp_delete = SICPDelete.Field()
    user_supplier_sicp_update = SupplierSICPUpdate.Field()
    user_supplier_sicp_text_editor_create = SICPTextEditorCreate.Field()

    user_diamond_sponsor_fee_create = UserDiamondSponsorFeeCreate.Field()
    user_diamond_sponsor_fee_update = UserDiamondSponsorFeeUpdate.Field()
    user_diamond_sponsor_fee_delete = UserDiamondSponsorFeeDelete.Field()

    supplier_flash_sale_click_count = SupplierFlashSaleClickCount.Field()
    supplier_product_click_count = SupplierProductClickCount.Field()
    supplier_product_create = SupplierProductCreate.Field()
    supplier_product_update = SupplierProductUpdate.Field()
    supplier_product_delete = SupplierProductDelete.Field()
    supplier_product_status_update = SupplierProductUpdateStatus.Field()
    supplier_product_confirmed_status_update = SupplierProductConfirmedStatusUpdate.Field()

    user_following_supplier_create = UserFollowingSupplierCreate.Field()
    user_following_supplier_update = UserFollowingSupplierUpdate.Field()

    user_rating_supplier_product_update = UserRatingSupplierProductUpdate.Field()
