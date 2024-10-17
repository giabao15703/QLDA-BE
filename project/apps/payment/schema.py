import django_filters
import graphene
import graphene_django_optimizer as gql_optimizer

from apps.auctions.models import AuctionSupplier
from apps.auctions.query import AuctionSupplierNode
from apps.core import Error
from apps.core import CustomNode, CustomizeFilterConnectionField
from apps.invoices.views import invoice_generate
from apps.master_data.models import Promotion, Bank, EmailTemplates, EmailTemplatesTranslation, PromotionUserUsed, PromotionApplyScope
from apps.master_data.schema import BankNode, send_mail_promotion
from apps.payment.error_code import PaymentError
from apps.payment.models import (
    BankTransfer,
    History,
    UserPayment,
    BankTransferHistory,
    BankTransferPaymentOrderAttached,
    HistoryPending,
    PaymentAuction,
    HistoryOnePay,
    BankTransferRefund,
    UserDiamondSponsorPayment,
)
from apps.sale_schema.models import ProfileFeaturesBuyer, ProfileFeaturesSupplier, SICPRegistration
from apps.users.models import (   
    Token,
    Supplier,
    Buyer,
    UserDiamondSponsor,
    UserDiamondSponsorFee,
)
from apps.order.models import (
    Order,
    OrderStatus
)
from datetime import datetime
import pytz
from django_filters import FilterSet, OrderingFilter
from django.core.mail import send_mail
from django.db import transaction
from django.template import Template, Context
from django.utils import timezone
from graphene import relay, ObjectType, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from decimal import Decimal

class ExtendedConnection(Connection):
    total_count = graphene.Int()

    class Meta:
        abstract = True

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

def send_mail_upgraded(user, scheme):
    language_code = user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code="ProfileUpgraded", language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code="ProfileUpgraded")
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": user.full_name,
                "scheme": scheme.name,
                "link": "https://auction.nextpro.io/account",
            }
        )
    )
    try:
        send_mail(email_template.title, messages, "NextPro <no-reply@nextpro.io>", [user.email], html_message=messages, fail_silently=True)
    except:
        print("fail mail")

def send_mail_sicp(user, scheme):
    language_code = user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code="SuccessfullySICP", language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code="SuccessfullySICP")
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": user.full_name,
                "scheme": scheme.name,
                "link": "https://auction.nextpro.io/accountt",
            }
        )
    )
    try:
        send_mail(email_template.title, messages, "NextPro <no-reply@nextpro.io>", [user.email], html_message=messages, fail_silently=True)
    except:
        print("fail mail")

def send_mail_paid_successfully(user, history):
    language_code = user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code="PaidSuccessfully", language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code="PaidSuccessfully")
    email_template = email_template.first()
    title = Template(email_template.title).render(Context({'order_no': history.order_no}))
    messages = Template(email_template.content).render(
        Context({"image": "https://api.nextpro.io/static/logo_mail.png", "name": user.full_name, "order_no": history.order_no,})
    )
    try:
        send_mail(title, messages, "NextPro <no-reply@nextpro.io>", [user.email], html_message=messages, fail_silently=True)
    except:
        print("fail mail")


def send_mail_received_bank_transfer(user, history):
    language_code = user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code="ReceivedBankTransfer", language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code="ReceivedBankTransfer")
    email_template = email_template.first()
    title = Template(email_template.title).render(Context({'order_no': history.order_no}))
    messages = Template(email_template.content).render(
        Context({"image": "https://api.nextpro.io/static/logo_mail.png", "name": user.full_name, "order_no": history.order_no,})
    )
    try:
        send_mail(title, messages, "NextPro <no-reply@nextpro.io>", [user.email], html_message=messages, fail_silently=True)
    except:
        print("fail mail")

# ----------------- query -------------------
class UserPaymentNode(DjangoObjectType):
    class Meta:
        model = UserPayment
        filter_fields = ['id']
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset


class HistoryFilter(FilterSet):
    date_from = django_filters.CharFilter(method='date_from_filter')
    date_to = django_filters.CharFilter(method='date_to_filter')
    amount_from = django_filters.CharFilter(method='amount_from_filter')
    amount_to = django_filters.CharFilter(method='amount_to_filter')
    user_type = django_filters.CharFilter(method='user_type_filter')
    full_name = django_filters.CharFilter(method='full_name_filter')
    transaction_description = django_filters.CharFilter(lookup_expr='icontains')
    order_no = django_filters.CharFilter(lookup_expr='icontains')
    admin_balance = django_filters.NumberFilter(method='admin_balance_filter')
    date = django_filters.CharFilter(method='date_filter')
    username = django_filters.CharFilter(method='username_filter')
    type = django_filters.CharFilter(method='type_filter')

    class Meta:
        model = History
        fields = ['id', 'type', 'status', 'balance', 'method_payment', 'amount']

    order_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('date', 'date'),
            ('type', 'type'),
            ('balance', 'balance'),
            ('status', 'status'),
            ('order_no', 'order_no'),
            ('user_payment__user__username', 'username'),
            ('user_payment__user__full_name', 'full_name'),
            ('amount', 'amount'),
            ('admin_balance', 'admin_balance'),
            ('transaction_description', 'transaction_description'),
            ('method_payment', 'method_payment'),
        )
    )

    def date_from_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(date__gte=value)
        return queryset

    def date_to_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        queryset = queryset.filter(date__lte=value)
        return queryset

    def amount_from_filter(self, queryset, name, value):
        queryset = queryset.filter(amount__gte=float(value))
        return queryset

    def amount_to_filter(self, queryset, name, value):
        queryset = queryset.filter(amount__lte=float(value))
        return queryset

    def user_type_filter(self, queryset, name, value):
        queryset = queryset.filter(user_payment__user__user_type=value)
        return queryset

    def full_name_filter(self, queryset, name, value):
        queryset = queryset.filter(user_payment__user__full_name__icontains=value)
        return queryset

    def admin_balance_filter(self, queryset, name, value):
        queryset = queryset.filter(admin_balance=value)
        return queryset

    def date_filter(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        value_to = value + timezone.timedelta(days=1)
        queryset = queryset.filter(date__range=(value, value_to))
        return queryset

    def username_filter(self, queryset, name, value):
        queryset = queryset.filter(user_payment__user__username__icontains=value)
        return queryset

    def type_filter(self, queryset, name, value):
        value = value.split(',')
        queryset = queryset.filter(type__in=value)
        return queryset

class HistoryConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    total_pending = graphene.Float()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_total_pending(root, info, **kwargs):
        try:
            user = GetToken.getToken(info).user
            histories = History.objects.filter(user_payment=user.user_payment, status=7)
            amount = 0
            for history in histories:
                amount += history.balance
            return amount
        except:
            return 0

class HistoryParentNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')
    supplier_status = graphene.Int()

    class Meta:
        model = History
        filterset_class = HistoryFilter
        convert_choices_to_enum = False
        interfaces = (relay.Node,)
        connection_class = HistoryConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter(is_parent=True).order_by('id'), info)
        return queryset

    def resolve_request_draft_invoice(self, info):
        if self.request_draft_invoice and hasattr(self.request_draft_invoice, 'url'):
            return info.context.build_absolute_uri(self.request_draft_invoice.url)
        else:
            return ''

    def resolve_invoice_receipt(self, info):
        if self.invoice_receipt and hasattr(self.invoice_receipt, 'url'):
            return info.context.build_absolute_uri(self.invoice_receipt.url)
        else:
            return ''

    def resolve_supplier_status(self, info):
        if self.type == 2:
            history = self
            if not self.is_parent:
                history = HistoryPending.objects.filter(history_pending=self).first().history
            auction_supplier = AuctionSupplier.objects.filter(auction=history.payment_auction.auction, user=self.user_payment.user).first()
            return auction_supplier.supplier_status
        return None

class HistoryPendingNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')
    history_parent = graphene.Field(HistoryParentNode)

    class Meta:
        model = History
        filterset_class = HistoryFilter
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = HistoryConnection

    def resolve_request_draft_invoice(self, info):
        if self.request_draft_invoice and hasattr(self.request_draft_invoice, 'url'):
            return info.context.build_absolute_uri(self.request_draft_invoice.url)
        else:
            return ''

    def resolve_history_parent(self, info):
        history = HistoryPending.objects.filter(history_pending=self).first().history
        return history

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter(is_parent=False).order_by('-id'), info)
        return queryset

class HistoryNode(DjangoObjectType):
    pk = graphene.Field(type=graphene.Int, source='id')
    history_pending = DjangoFilterConnectionField(HistoryPendingNode)
    remain_amount = graphene.Float()
    supplier_status = graphene.Int()

    class Meta:
        model = History
        filterset_class = HistoryFilter
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = HistoryConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter(is_parent=True).order_by('-id'), info)
        return queryset

    def resolve_request_draft_invoice(self, info):
        if self.request_draft_invoice and hasattr(self.request_draft_invoice, 'url'):
            return info.context.build_absolute_uri(self.request_draft_invoice.url)
        else:
            return ''

    def resolve_invoice_receipt(self, info):
        if self.invoice_receipt and hasattr(self.invoice_receipt, 'url'):
            return info.context.build_absolute_uri(self.invoice_receipt.url)
        else:
            return ''

    def resolve_history_pending(self, info):
        history_pending = HistoryPending.objects.filter(history=self).order_by('id')
        y = []
        for i in history_pending:
            y.append(i.history_pending.id)
        return History.objects.filter(id__in=y).order_by('id')

    def resolve_remain_amount(self, info):
        if self.status == 7 and self.type == 1:
            histories_pending_list = map(lambda x: x.get('history_pending'), HistoryPending.objects.filter(history=self).values('history_pending'))
            result = History.objects.filter(id__in=histories_pending_list, status=7)
            amount = 0
            if self.status == 7:
                amount = self.balance
            for history_pending in result:
                amount += history_pending.balance
            remain_amount = self.amount - amount
            if self.status == 2 or remain_amount <= 0:
                return 0
            return remain_amount
        else:
            return None

    def resolve_supplier_status(self, info):
        if self.type == 2:
            history = self
            if not self.is_parent:
                history = HistoryPending.objects.filter(history_pending=self).first().history
            if hasattr(history, "payment_auction"):
                auction_supplier = AuctionSupplier.objects.filter(auction=history.payment_auction.auction, user=self.user_payment.user).first()
                return auction_supplier.supplier_status
        return None

class BankTransferNode(DjangoObjectType):
    class Meta:
        model = BankTransfer
        filter_fields = ['id']
        convert_choices_to_enum = False
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    def resolve_payment_order_attached(self, info):
        if self.payment_order_attached and hasattr(self.payment_order_attached, 'url'):
            return info.context.build_absolute_uri(self.payment_order_attached.url)
        else:
            return ''

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset

class BankTransferHistoryNode(DjangoObjectType):
    class Meta:
        model = BankTransferHistory
        filter_fields = ['id']
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset

class BankTransferPaymentOrderAttachedNode(DjangoObjectType):
    class Meta:
        model = BankTransferPaymentOrderAttached
        filter_fields = ['id']
        interfaces = (relay.Node,)

    def resolve_file(self, info):
        if self.file and hasattr(self.file, 'url'):
            return info.context.build_absolute_uri(self.file.url)
        else:
            return ''

class PaymentAuctionNode(DjangoObjectType):
    class Meta:
        model = PaymentAuction
        filter_fields = ['id']
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset

class HistoryOnePayNode(DjangoObjectType):
    class Meta:
        model = HistoryOnePay
        filter_fields = ['id']
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = gql_optimizer.query(queryset.filter().order_by('id'), info)
        return queryset

class BankTransferAccount(graphene.ObjectType):
    bank = graphene.Field(BankNode)
    bank_number = graphene.String()
    amount = graphene.Float()


# --------------------------mutation-------------------

class PromotionApplyScopeWalletInput(graphene.Enum):
    FOR_SUPPLIER_PROFILE_FEATURES = PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES
    FOR_SUPPLIER_SICP = PromotionApplyScope.FOR_SUPPLIER_SICP
class PromotionWalletInput(graphene.InputObjectType):
    promotion_id = graphene.String()
    promotion_type = PromotionApplyScopeWalletInput()


class BankTransferInput(graphene.InputObjectType):
    bank_information = graphene.String()
    order_number = graphene.String()
    bank_account_number = graphene.String(required=True)
    bank = graphene.String(required=True)
    day_of_payment = graphene.String(required=True)
    payment_order_attached = graphene.List(Upload)
    amount = graphene.Float(required=True)
    auction_number = graphene.String()
    diamond_sponsor = graphene.String()
    order = graphene.String()


class BankTransferForZeroInput(graphene.InputObjectType):
    amount = graphene.Float(required=True)
    diamond_sponsor = graphene.String()
    promotion = graphene.String()


class PaymentBankTransferInput(graphene.InputObjectType):
    type = graphene.Int(required=True)
    profile_features = graphene.String()
    sicp_registration = graphene.String()
    promotion = graphene.String()
    promotion_list = graphene.List(PromotionWalletInput)


class BankTransferCreate(graphene.Mutation):

    status = graphene.Boolean()
    bank_transfer = graphene.Field(BankTransferNode)
    error = graphene.Field(Error)

    class Arguments:
        bank_transfer_input = BankTransferInput(required=True)
        payment = PaymentBankTransferInput(required=True)

    @transaction.atomic
    def mutate(root, info, payment, bank_transfer_input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)

            orderPayment = Order.objects.filter(id=bank_transfer_input.order).first()
            diamond_sponsor = UserDiamondSponsor.objects.filter(id=bank_transfer_input.diamond_sponsor).first()
            diamond_sponsor_fee = UserDiamondSponsorFee.objects.all().first()

            if diamond_sponsor_fee is None:
                return BankTransferCreate(
                    status=False,
                    error=Error(code="PAYMENT_14", message=PaymentError.PAYMENT_14)
                )
            bank_transfer = BankTransfer(
                user=user,
                bank_information=bank_transfer_input.bank_information,
                order_number=bank_transfer_input.order_number,
                bank_account_number=bank_transfer_input.bank_account_number,
                bank_id=bank_transfer_input.bank,
                day_of_payment=bank_transfer_input.day_of_payment,
                amount=bank_transfer_input.amount,
                auction_number=bank_transfer_input.auction_number,
                diamond_sponsor=diamond_sponsor,
                order=orderPayment,
            )
            bank_transfer.save()
            if bank_transfer_input.payment_order_attached is not None and len(bank_transfer_input.payment_order_attached) > 0:
                for file in bank_transfer_input.payment_order_attached:
                    BankTransferPaymentOrderAttached.objects.create(bank_transfer=bank_transfer, file=file)

            user_payment = UserPayment.objects.filter(user=user).first()
            detail = []
            is_topup = False
            total = 0
            data = {}

            order_no = History.objects.filter().count() + 1
            order_no = '70' + str(order_no).zfill(4)
            amount_discount = None
            # payment
            if payment.type == 1:
                promotion = None
                promotion_intansce = None
                if payment.promotion is not None:
                    promotion = payment.promotion
                    promotion_intansce = Promotion.objects.filter(id=promotion).first()
                    if promotion_intansce is None:
                        error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                        raise GraphQLError('Promotion code has been deactivated ')

                    if promotion_intansce.status == False:
                        error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                        raise GraphQLError('Promotion code has been deactivated ')
                now = timezone.now()
                if payment.promotion_list:
                    if user.isSupplier():
                        for promotion in payment.promotion_list:
                            if promotion.promotion_type is None:
                                error = Error(code="PAYMENT_17", message=PaymentError.PAYMENT_17)
                                raise GraphQLError(PaymentError.PAYMENT_17)
                            if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_SICP \
                                and not Promotion.objects.filter(
                                    id = promotion.promotion_id,
                                    valid_from__lte = now,
                                    valid_to__gte = now,
                                    apply_scope__in = [PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_SICP]
                                ).exists():
                                    error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                                    raise GraphQLError(PaymentError.PAYMENT_15)
                            if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES\
                                and not Promotion.objects.filter(
                                    id = promotion.promotion_id,
                                    valid_from__lte = now,
                                    valid_to__gte = now,
                                    apply_scope__in = [PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES]
                                ).exists():
                                    error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                                    raise GraphQLError(PaymentError.PAYMENT_15)
                    elif user.isBuyer():
                        if not all(
                            Promotion.objects.filter(
                                id = promotion.promotion_id,
                                valid_from__lte = now,
                                valid_to__gte = now,
                                apply_scope = PromotionApplyScope.FOR_BUYER
                            ).exists() for promotion in payment.promotion_list
                        ):
                            error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                            raise GraphQLError(PaymentError.PAYMENT_15)

                admin_balance = 0
                if user.isSupplier():
                    supplier = Supplier.objects.filter(user=user).first()
                    amount_profile_features = 0
                    amount_sicp_registration = 0
                    profile_features = supplier.profile_features
                    sicp_registration = supplier.sicp_registration

                    if payment.profile_features is not None and payment.sicp_registration is not None:
                        profile_features_id = int(payment.profile_features)
                        sicp_registration_id = int(payment.sicp_registration)

                        if BankTransferHistory.objects.filter(
                            profile_features_supplier_id=profile_features_id,
                            sicp_registration_id=sicp_registration_id,
                            history__status=1,
                            history__user_payment=user_payment,
                        ).exists():
                            error = Error(code="PAYMENT_01", message=PaymentError.PAYMENT_01)
                            raise GraphQLError("The transaction is waiting for the administrator to confirm")

                        if supplier.profile_features_id != profile_features_id:
                            profile_features = ProfileFeaturesSupplier.objects.filter(id=profile_features_id).first()
                            amount_profile_features = profile_features.base_rate_full_year
                            if payment.promotion_list:
                                for promotion in payment.promotion_list:
                                    if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES:
                                        promotion_intansce = Promotion.objects.get(id = promotion.promotion_id)
                                        amount_profile_features = round(amount_profile_features - (amount_profile_features * promotion_intansce.discount) / 100)
                            detail.append(
                                {
                                    'description': "Profile Features",
                                    'quantity': 1,
                                    'unit_price': amount_profile_features,
                                    'total_amount': amount_profile_features,
                                }
                            )
                        if supplier.sicp_registration_id != sicp_registration_id:
                            sicp_registration = SICPRegistration.objects.filter(id=sicp_registration_id).first()
                            amount_sicp_registration = sicp_registration.total_amount
                            if payment.promotion_list:
                                for promotion in payment.promotion_list:
                                    if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_SICP:
                                        promotion_intansce = Promotion.objects.get(id = promotion.promotion_id)
                                        amount_sicp_registration = round(amount_sicp_registration - (amount_sicp_registration * promotion_intansce.discount) / 100)
                            detail.append(
                                {
                                    'description': "Sicp Registration",
                                    'quantity': 1,
                                    'unit_price': amount_sicp_registration,
                                    'total_amount': amount_sicp_registration,
                                }
                            )
                            
                        if supplier.sicp_registration_id == sicp_registration_id and supplier.profile_features_id == profile_features_id:
                            error = Error(code="PAYMENT_02", message=PaymentError.PAYMENT_02)
                            raise GraphQLError("You must upgrade profile features or sicp registration ")

                        discount = 0
                        promotion = None
                        amount_payment = amount_profile_features + amount_sicp_registration
                        if payment.promotion is not None:
                            promotion = payment.promotion
                            promotion_intansce = Promotion.objects.get(id=promotion)
                            if promotion_intansce.status == False:
                                error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                                raise GraphQLError('Promotion code has been deactivated')
                            discount = promotion_intansce.discount
                            amount_discount = round((amount_payment * discount) / 100)
                            detail.append(
                                {
                                    'description': promotion_intansce.description,
                                    'quantity': 1,
                                    'unit_price': amount_discount,
                                    'total_amount': amount_discount,
                                }
                            )

                        supplier.promotion_id = promotion
                        supplier.save()

                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)

                        amount_topup = bank_transfer.amount - amount_payment
                        if amount_payment > bank_transfer.amount:
                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Upgrade Profile ",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                amount=amount_payment,
                                admin_balance=admin_balance,
                                is_parent=True,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                profile_features_supplier=profile_features,
                                sicp_registration=sicp_registration,
                                is_pending=True,
                                promotion_id=promotion,
                            )

                        else:

                            if amount_topup > 0:
                                admin_balance = amount_topup

                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Upgrade Profile",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                admin_balance=admin_balance,
                                amount=amount_payment,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                profile_features_supplier=profile_features,
                                sicp_registration=sicp_registration,
                                promotion_id=promotion,
                            )

                    if diamond_sponsor is not None:
                        if diamond_sponsor_fee.fee >= bank_transfer_input.amount:
                            error = Error(code="PAYMENT_11", message=PaymentError.PAYMENT_11)
                            raise GraphQLError("Invalid amount")
                        if UserDiamondSponsorPayment.objects.filter(user_diamond_sponsor=diamond_sponsor).exists():
                            error = Error(code="PAYMENT_13", message=PaymentError.PAYMENT_13)
                            raise GraphQLError("The diamond spnosor has been paid")

                        discount = 0
                        promotion = None
                        amount_payment = diamond_sponsor_fee.fee
                        if payment.promotion is not None:
                            promotion = payment.promotion
                            promotion_intansce = Promotion.objects.get(id=promotion)
                            if promotion_intansce.status == False:
                                error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                                raise GraphQLError('Promotion code has been deactivated')
                            discount = promotion_intansce.discount
                            amount_discount = round((amount_payment * discount) / 100)
                            detail.append(
                                {
                                    'description': promotion_intansce.description,
                                    'quantity': 1,
                                    'unit_price': amount_discount,
                                    'total_amount': amount_discount,
                                }
                            )

                        supplier.promotion_id = promotion
                        supplier.save()

                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)

                        amount_topup = bank_transfer.amount - amount_payment
                        if amount_payment > bank_transfer.amount:
                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="DiamondSponsor",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                amount=amount_payment,
                                admin_balance=admin_balance,
                                is_parent=True,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                is_pending=True,
                                promotion_id=promotion,
                            )

                            diamond_sponsor_payment = UserDiamondSponsorPayment.objects.create(
                                user_diamond_sponsor=diamond_sponsor,
                                charge_amount=bank_transfer.amount,
                                history=history,
                                method_payment=2,
                            )
                        else:
                            if amount_topup > 0:
                                admin_balance = amount_topup

                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="DiamondSponsor",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                admin_balance=admin_balance,
                                amount=amount_payment,
                            )
                            
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                promotion_id=promotion,
                            )

                            diamond_sponsor_payment = UserDiamondSponsorPayment.objects.create(
                                user_diamond_sponsor=diamond_sponsor,
                                charge_amount=bank_transfer.amount,
                                history=history,
                                method_payment=2,
                            )

                    if bank_transfer_input.order is not None:
                        order = Order.objects.filter(order_id = bank_transfer_input.order).first()
                        if order is None:
                            error = Error(code="PAYMENT_21", message=PaymentError.PAYMENT_21)
                            raise GraphQLError("This order does not exists.")
                        discount = 0
                        promotion = None
                        amount_payment = order.amount
                        if payment.promotion is not None:
                            promotion = payment.promotion
                            promotion_intansce = Promotion.objects.get(id=promotion)
                            if promotion_intansce.status == False:
                                error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                                raise GraphQLError('Promotion code has been deactivated')
                            discount = promotion_intansce.discount
                            amount_discount = round((amount_payment * discount) / 100)
                            detail.append(
                                {
                                    'description': promotion_intansce.description,
                                    'quantity': 1,
                                    'unit_price': amount_discount,
                                    'total_amount': amount_discount,
                                }
                            )

                        supplier.promotion_id = promotion
                        supplier.save()

                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)

                        amount_topup = bank_transfer.amount - amount_payment
                        if amount_payment > bank_transfer.amount:
                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Order",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                amount=amount_payment,
                                admin_balance=admin_balance,
                                is_parent=True,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                is_pending=True,
                                promotion_id=promotion,
                            )
                        else:
                            if amount_topup > 0:
                                admin_balance = amount_topup

                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Order",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                admin_balance=admin_balance,
                                amount=amount_payment,
                            )
                            
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                promotion_id=promotion,
                            )
                        order.order_status = OrderStatus.PAID.value
                        order.save()

                elif user.isBuyer():
                    discount = 0
                    buyer = Buyer.objects.filter(user=user).first()
                    profile_features_id = int(payment.profile_features)
                    profile_features = ProfileFeaturesBuyer.objects.filter(id=profile_features_id).first()
                    
                    if BankTransferHistory.objects.filter(
                        profile_features_buyer_id=profile_features_id, history__status=1, history__user_payment=user_payment,
                    ).exists():
                        error = Error(code="PAYMENT_01", message=PaymentError.PAYMENT_01)
                        raise GraphQLError("The transaction is waiting for the administrator to confirm")

                    if bank_transfer_input.order is not None:
                        order = Order.objects.filter(id = bank_transfer_input.order).first()
                        if order is None:
                            error = Error(code="PAYMENT_21", message=PaymentError.PAYMENT_21)
                            raise GraphQLError("This order does not exists.")
                        promotion = None
                        amount_payment = order.totalAmount
                        if payment.promotion is not None:
                            promotion = payment.promotion
                            promotion_intansce = Promotion.objects.get(id=promotion)
                            if promotion_intansce.status == False:
                                error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                                raise GraphQLError('Promotion code has been deactivated ')
                            discount = promotion_intansce.discount
                            amount_discount = round((amount_payment * discount) / 100)
                            detail.append(
                                {
                                    'description': promotion_intansce.description,
                                    'quantity': 1,
                                    'unit_price': amount_discount,
                                    'total_amount': amount_discount,
                                }
                            )

                        buyer.promotion_id = promotion
                        buyer.save()
                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * Decimal('0.1'))
                        amount_topup = bank_transfer.amount - amount_payment

                        if amount_payment > bank_transfer.amount:
                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Order",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                amount=amount_payment,
                                admin_balance=admin_balance,
                                is_parent=True,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                profile_features_buyer=profile_features,
                                is_pending=True,
                                promotion_id=promotion,
                            )
                        else:
                            if amount_topup > 0:
                                admin_balance = amount_topup

                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Order",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                amount=amount_payment,
                                admin_balance=admin_balance,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer, history=history, profile_features_buyer=profile_features, promotion_id=promotion
                            )
                        order.order_status = OrderStatus.PAID.value
                        order.save()
                    else:
                        if buyer.profile_features_id != profile_features_id:
                            profile_features = ProfileFeaturesBuyer.objects.filter(id=profile_features_id).first()
                            amount_profile_features = profile_features.total_fee_year
                            if payment.promotion_list:
                                for promotion in payment.promotion_list:
                                    promotion_intansce = Promotion.objects.get(id = promotion.promotion_id)
                                    amount_profile_features = round(amount_profile_features* (100 - promotion.discount) / 100)

                            detail.append(
                                {
                                    'description': "Profile Features",
                                    'quantity': 1,
                                    'unit_price': amount_profile_features,
                                    'total_amount': amount_profile_features,
                                }
                            )
                        else:
                            error = Error(code="PAYMENT_04", message=PaymentError.PAYMENT_04)

                            raise GraphQLError("You must upgrade profile features")
                        
                        promotion = None
                        amount_payment = amount_profile_features
                        if payment.promotion is not None:
                            promotion = payment.promotion
                            promotion_intansce = Promotion.objects.get(id=promotion)
                            if promotion_intansce.status == False:
                                error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                                raise GraphQLError('Promotion code has been deactivated ')
                            discount = promotion_intansce.discount
                            amount_discount = round((amount_payment * discount) / 100)
                            detail.append(
                                {
                                    'description': promotion_intansce.description,
                                    'quantity': 1,
                                    'unit_price': amount_discount,
                                    'total_amount': amount_discount,
                                }
                            )

                        buyer.promotion_id = promotion
                        buyer.save()
                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)
                        amount_topup = bank_transfer.amount - amount_payment

                        if amount_payment > bank_transfer.amount:
                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Upgrade Profile ",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                amount=amount_payment,
                                admin_balance=admin_balance,
                                is_parent=True,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer,
                                history=history,
                                profile_features_buyer=profile_features,
                                is_pending=True,
                                promotion_id=promotion,
                            )
                        else:
                            if amount_topup > 0:
                                admin_balance = amount_topup

                            history = History.objects.create(
                                user_payment=user_payment,
                                type=1,
                                transaction_description="Upgrade Profile",
                                balance=bank_transfer.amount,
                                status=1,
                                method_payment=2,
                                order_no=order_no,
                                amount=amount_payment,
                                admin_balance=admin_balance,
                            )
                            bank_transfer_history = BankTransferHistory.objects.create(
                                bank_transfer=bank_transfer, history=history, profile_features_buyer=profile_features, promotion_id=promotion
                            )
                else:
                    error = Error(code="PAYMENT_05", message=PaymentError.PAYMENT_05)
                    raise GraphQLError("You must be buyer or supplier")
            # Topup
            elif payment.type == 3:
                detail.append(
                    {'description': "Topup", 'quantity': 1, 'unit_price': bank_transfer.amount, 'total_amount': bank_transfer.amount,}
                )
                history = History.objects.create(
                    user_payment=user_payment,
                    type=3,
                    transaction_description="Topup",
                    balance=bank_transfer.amount,
                    status=1,
                    method_payment=2,
                    order_no=order_no,
                )
                bank_transfer_history = BankTransferHistory.objects.create(bank_transfer=bank_transfer, history=history)
                sub_total = bank_transfer.amount
                is_topup = True

            else:
                raise GraphQLError("Type does not exists ")
            # invoice
            if payment.type != 3:
                data = {
                    'user': user,
                    'invoice_no': history.order_no,
                    'invoice_date': datetime.strftime(history.date, '%d-%m-%Y'),
                    'detail_list': detail,
                    'sub_total': sub_total,
                    'is_topup': is_topup,
                }
                invoice_generate(data)
                request_draft_invoice = f'''{user.id}/{history.order_no}/draft_invoice.pdf'''
                history.request_draft_invoice = request_draft_invoice
            history.save()
            send_mail_received_bank_transfer(user, history)
            return BankTransferCreate(status=True, bank_transfer=bank_transfer)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return BankTransferCreate(status=False, error=error)


class BankTransferForZeroCreate(graphene.Mutation):
    status = graphene.Boolean()
    bank_transfer = graphene.Field(BankTransferNode)
    error = graphene.Field(Error)

    class Arguments:
        bank_transfer_for_zero_input = BankTransferForZeroInput(required=True)

    @transaction.atomic
    def mutate(root, info, bank_transfer_for_zero_input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)

            if bank_transfer_for_zero_input.amount > 0:
                error = Error(code="PAYMENT_20", message=PaymentError.PAYMENT_20)
                raise GraphQLError('The amount should be zero.')

            order_no = History.objects.filter().count() + 1
            order_no = '70' + str(order_no).zfill(4)
            diamond_sponsor = UserDiamondSponsor.objects.filter(id=bank_transfer_for_zero_input.diamond_sponsor).first()
            bank_transfer = BankTransfer(
                user=user,
                bank_information='Zero payment',
                order_number=None,
                bank_account_number='123456789',
                bank_id=1,
                day_of_payment=datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')),
                amount=0,
                auction_number=None,
                diamond_sponsor=diamond_sponsor,
            )
            bank_transfer.save()

            # validation Promotion
            promotion = bank_transfer_for_zero_input.promotion
            if promotion is not None:
                promotion_instance = Promotion.objects.get(id=promotion)
                if promotion_instance is not None:
                    if not promotion_instance.status:
                        error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                        raise GraphQLError('Promotion code has been deactivated')
                else:
                    error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                    raise GraphQLError('Promotion code does not exists or been expired')

            else:
                error = Error(code="PAYMENT_18", message=PaymentError.PAYMENT_18)
                raise GraphQLError('Promotion code is empty.')

            # validation User Payment
            user_payment = UserPayment.objects.filter(user=user).first()
            if user_payment is None:
                error = Error(code="PAYMENT_19", message=PaymentError.PAYMENT_19)
                raise GraphQLError('User payment does not exists.')

            history = History.objects.create(
                user_payment=user_payment,
                type=1,
                transaction_description="DiamondSponsor",
                balance=bank_transfer.amount,
                status=2,
                method_payment=2,
                order_no=order_no,
                amount=0,
                admin_balance=0,
                is_parent=True,
            )

            bank_transfer_history = BankTransferHistory.objects.create(
                bank_transfer=bank_transfer,
                history=history,
                is_pending=False,
                promotion_id=promotion,
            )

            diamond_sponsor_payment = UserDiamondSponsorPayment.objects.create(
                user_diamond_sponsor=diamond_sponsor,
                charge_amount=bank_transfer.amount,
                history=history,
                method_payment=2,
            )
            return BankTransferForZeroCreate(status=True, bank_transfer=bank_transfer)

        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return BankTransferForZeroCreate(status=False, error=error)


class BankTransferPending(graphene.Mutation):
    class Arguments:
        bank_transfer_input = BankTransferInput(required=True)
        history_id = graphene.String(required=True)

    status = graphene.Boolean()
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    def mutate(root, info, history_id, bank_transfer_input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            bank_transfer = BankTransfer(
                user=user,
                bank_information=bank_transfer_input.bank_information,
                order_number=bank_transfer_input.order_number,
                bank_account_number=bank_transfer_input.bank_account_number,
                bank_id=bank_transfer_input.bank,
                day_of_payment=bank_transfer_input.day_of_payment,
                amount=bank_transfer_input.amount,
                auction_number=bank_transfer_input.auction_number,
            )
            bank_transfer.save()

            for file in bank_transfer_input.payment_order_attached:
                BankTransferPaymentOrderAttached.objects.create(bank_transfer=bank_transfer, file=file)
            user_payment = UserPayment.objects.filter(user=user).first()
            detail = [
                {'description': "Upgrade Profile Pending", 'quantity': 1, 'unit_price': bank_transfer.amount, 'total_amount': bank_transfer.amount,}
            ]
            order_no = History.objects.filter().count() + 1
            order_no = '70' + str(order_no).zfill(4)
            # payment
            history = History.objects.filter(id=history_id).first()
            histories_pending_list = map(lambda x: x.get('history_pending'), HistoryPending.objects.filter(history=history).values('history_pending'))
            histories_pending = History.objects.filter(id__in=histories_pending_list, status=7)
            amount = 0
            if history.status == 7:
                amount = history.balance

            for history_pending in histories_pending:
                amount += history_pending.balance
            remain_amount = history.amount - amount
            if remain_amount < 0:
                remain_amount = 0
            history_pending = History.objects.create(
                user_payment=user_payment,
                type=1,
                transaction_description="Upgrade Profile Pending",
                balance=bank_transfer.amount,
                status=1,
                method_payment=2,
                order_no=order_no,
                amount=remain_amount,
                is_parent=False,
            )
            bank_transfer_history = BankTransferHistory.objects.create(bank_transfer=bank_transfer, history=history_pending, is_pending=True,)
            HistoryPending.objects.create(history=history, history_pending=history_pending)

            # invoice
            data = {
                'user': user,
                'invoice_no': history_pending.order_no,
                'invoice_date': datetime.strftime(history.date, '%d-%m-%Y'),
                'detail_list': detail,
                'sub_total': bank_transfer.amount,
                'is_topup': True,
            }
            invoice_generate(data)
            request_draft_invoice = f'''{user.id}/{history_pending.order_no}/draft_invoice.pdf'''
            history_pending.request_draft_invoice = request_draft_invoice
            history_pending.save()
            send_mail_received_bank_transfer(user, history_pending)
            return BankTransferPending(status=True, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return BankTransferPending(error=error, status=False)


class BanksTransferDeposit(graphene.Mutation):
    status = graphene.Boolean()
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    class Arguments:
        bank_transfer_input = BankTransferInput(required=True)
        history_id = graphene.String(required=True)

    def mutate(root, info, history_id, bank_transfer_input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            user_payment = UserPayment.objects.filter(user=user).first()
            history = History.objects.filter(id=history_id).first()
            auction_supplier = AuctionSupplier.objects.filter(auction=history.payment_auction.auction, user=user).first()
            if history.status not in (1, 2, 6) or auction_supplier.supplier_status not in (1, 4):
                error = Error(code="PAYMENT_07", message=PaymentError.PAYMENT_07)
                raise GraphQLError('The transaction is done')
            bank_transfer = BankTransfer(
                user=user,
                bank_information=bank_transfer_input.bank_information,
                order_number=bank_transfer_input.order_number,
                bank_account_number=bank_transfer_input.bank_account_number,
                bank_id=bank_transfer_input.bank,
                day_of_payment=bank_transfer_input.day_of_payment,
                amount=bank_transfer_input.amount,
                auction_number=bank_transfer_input.auction_number,
            )
            bank_transfer.save()
            for file in bank_transfer_input.payment_order_attached:
                BankTransferPaymentOrderAttached.objects.create(bank_transfer=bank_transfer, file=file)
            admin_balance = history.admin_balance

            if history.status == 6 and history.is_parent == True:
                order_no = History.objects.filter().count() + 1
                order_no = '70' + str(order_no).zfill(4)
                payment_auction = PaymentAuction.objects.filter(history=history).first()
                amount_topup = bank_transfer.amount - history.amount
                if amount_topup > 0:
                    admin_balance += amount_topup
                history_bank = History.objects.create(
                    user_payment=user_payment,
                    type=2,
                    transaction_description=f'''Deposit {payment_auction.auction.item_code}''',
                    balance=bank_transfer.amount,
                    status=1,
                    method_payment=2,
                    order_no=order_no,
                    amount=history.amount,
                    is_parent=True,
                    admin_balance=admin_balance,
                )
                PaymentAuction.objects.create(
                    auction=payment_auction.auction,
                    charge_amount=payment_auction.charge_amount,
                    refund_amount=payment_auction.refund_amount,
                    history=history_bank,
                )

                amount_payment = round(history.amount / 1.1)
                detail = [
                    {
                        'description': f'''Deposit {payment_auction.auction.item_code}''',
                        'quantity': 1,
                        'unit_price': amount_payment,
                        'total_amount': amount_payment,
                    }
                ]
                data = {
                    'user': user_payment.user,
                    'invoice_no': history_bank.order_no,
                    'invoice_date': datetime.strftime(history_bank.date, '%d-%m-%Y'),
                    'detail_list': detail,
                    'sub_total': amount_payment,
                    'is_topup': False,
                }

                invoice_generate(data)
                request_draft_invoice = f'''{user_payment.user.id}/{history_bank.order_no}/draft_invoice.pdf'''
                history_bank.request_draft_invoice = request_draft_invoice
                history_bank.save()
                history.status = 10
                history.save()

                bank_transfer_history = BankTransferHistory.objects.create(bank_transfer=bank_transfer, history=history_bank)
                send_mail_received_bank_transfer(user_payment.user, history_bank)
                history = history_bank

            # pending
            elif auction_supplier.supplier_status in (1, 4) and BankTransferHistory.objects.filter(history=history).exists() and history.status == 2:
                order_no = History.objects.filter().count() + 1
                order_no = '70' + str(order_no).zfill(4)
                history_pending = History.objects.create(
                    user_payment=user_payment,
                    type=2,
                    transaction_description="Deposit Partial",
                    balance=bank_transfer.amount,
                    status=1,
                    method_payment=2,
                    order_no=order_no,
                    amount=history.amount,
                    is_parent=False,
                    admin_balance=history.admin_balance,
                )
                amount_payment = round(history.amount / 1.1)
                detail = [
                    {
                        'description': f'''Deposit {auction_supplier.auction.item_code}''',
                        'quantity': 1,
                        'unit_price': amount_payment,
                        'total_amount': amount_payment,
                    }
                ]
                data = {
                    'user': user_payment.user,
                    'invoice_no': history_pending.order_no,
                    'invoice_date': datetime.strftime(history_pending.date, '%d-%m-%Y'),
                    'detail_list': detail,
                    'sub_total': amount_payment,
                    'is_topup': False,
                }

                invoice_generate(data)
                request_draft_invoice = f'''{user_payment.user.id}/{history_pending.order_no}/draft_invoice.pdf'''
                history_pending.request_draft_invoice = request_draft_invoice
                history_pending.save()
                HistoryPending.objects.create(history=history, history_pending=history_pending)
                bank_transfer_history = BankTransferHistory.objects.create(bank_transfer=bank_transfer, history=history_pending, is_pending=True)
                auction_supplier.save()
                send_mail_received_bank_transfer(user_payment.user, history_pending)
            # new
            else:
                history.balance = bank_transfer.amount

                amount_topup = bank_transfer.amount - history.amount
                if amount_topup > 0:
                    admin_balance += amount_topup
                    history.admin_balance = admin_balance
                auction_supplier.save()
                sub_total = round(history.amount / 1.1)
                bank_transfer_history = BankTransferHistory.objects.create(bank_transfer=bank_transfer, history=history,)
                send_mail_received_bank_transfer(user_payment.user, history)

            history.method_payment = 2
            history.save()
            return BanksTransferDeposit(status=True, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return BanksTransferDeposit(error=error, status=False)


class PaymentPendingCheck(graphene.Mutation):
    class Arguments:
        profile_features = graphene.String()
        sicp_registration = graphene.String()
        diamond_sponsor = graphene.String()
        order = graphene.String()

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, profile_features=None, sicp_registration=None, diamond_sponsor=None, order=None):
        try:
            user = GetToken.getToken(info).user
            status = True
            if user.isBuyer():
                order_check = (
                    BankTransferHistory.objects.filter(
                        bank_transfer__order=order,
                        history__status__in=[1, 7],
                        history__user_payment=user.user_payment,
                        history__is_parent=True,
                    ).exists()
                )

                profile_features_check = (
                    BankTransferHistory.objects.filter(
                        profile_features_buyer_id=profile_features,
                        history__status__in=[1, 7],
                        history__user_payment=user.user_payment,
                        history__is_parent=True,
                    ).exists()
                )

                if order is not None:
                    if order_check:
                        status = False
                else:
                    if profile_features_check:
                        status = False

            if user.isSupplier():
                profile_features_check = (
                    BankTransferHistory.objects.filter(
                        profile_features_supplier_id=profile_features,
                        history__status__in=[1, 7],
                        history__user_payment=user.user_payment,
                        history__is_parent=True,
                    ).exists()
                    and user.supplier.profile_features_id != int(profile_features)
                )
                
                sicp_registration_check = (
                    BankTransferHistory.objects.filter(
                        sicp_registration_id=sicp_registration,
                        history__status__in=[1, 7],
                        history__user_payment=user.user_payment,
                        history__is_parent=True,
                    ).exists()
                    and user.supplier.sicp_registration_id != int(sicp_registration)
                )
                
                diamond_sponsor_check = (
                    BankTransferHistory.objects.filter(
                        bank_transfer__diamond_sponsor=diamond_sponsor,
                        history__status__in=[1, 7],
                        history__user_payment=user.user_payment,
                        history__is_parent=True,
                    ).exists()
                )

                if diamond_sponsor is not None:
                    if diamond_sponsor_check:
                        status = False
                else:
                    if (
                        BankTransferHistory.objects.filter(
                            profile_features_supplier_id=profile_features,
                            sicp_registration_id=sicp_registration,
                            history__status__in=[1, 7],
                            history__user_payment=user.user_payment,
                            history__is_parent=True,
                        ).exists()
                        or profile_features_check
                        or sicp_registration_check
                    ):
                        status = False
            return PaymentPendingCheck(status=status)
        except Exception as err:
            transaction.set_rollback(True)
            return PaymentPendingCheck(err)


class WalletInput(graphene.InputObjectType):
    auction_number = graphene.String()
    type = graphene.Int(required=True)
    profile_features = graphene.String()
    sicp_registration = graphene.String()
    promotion = graphene.String()
    method_payment = graphene.Int(required=True)
    notes = graphene.String()
    diamond_sponsor=graphene.String()
    promotion_list = graphene.List(PromotionWalletInput)

class WalletPayment(graphene.Mutation):
    class Arguments:
        wallet = WalletInput(required=True)

    status = graphene.Boolean()
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    def mutate(root, info, wallet):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            user_payment = UserPayment.objects.filter(user=user).first()
            order_no = History.objects.filter().count() + 1
            order_no = '70' + str(order_no).zfill(4)
            upgraded_profile = None
            sicp_email = None
            # payment
            discount_promotion = None
            discountContent = None
            promotion_intansce = None

            profile_name = None
            profile_feature_name = None
            sicp_name = None
            profile_amount = 0
            profile_feature_mount = 0
            sicp_amount = 0
            now = timezone.now()

            if wallet.promotion is not None:
                promotion_intansce = Promotion.objects.filter(
                    id = wallet.promotion,
                    valid_from__lte = now,
                    valid_to__gte = now
                    ).first()
                if promotion_intansce is None:
                    error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                    raise GraphQLError("Promotion code does not exists or been expired")
                if user.isBuyer() and not promotion_intansce.apply_for_buyer:
                    error = Error(code="PAYMENT_16", message=PaymentError.PAYMENT_16)
                    raise GraphQLError("You cannot use this promotion code")
                if user.isSupplier() and not promotion_intansce.apply_for_supplier:
                    error = Error(code="PAYMENT_16", message=PaymentError.PAYMENT_16)
                    raise GraphQLError("You cannot use this promotion code")

            if wallet.promotion_list:
                if user.isSupplier():
                    for promotion in wallet.promotion_list:
                        if promotion.promotion_type is None:
                            error = Error(code="PAYMENT_17", message=PaymentError.PAYMENT_17)
                            raise GraphQLError(PaymentError.PAYMENT_17)
                        if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_SICP \
                            and not Promotion.objects.filter(
                                id = promotion.promotion_id,
                                valid_from__lte = now,
                                valid_to__gte = now,
                                apply_scope__in = [PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_SICP]
                            ).exists():
                                error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                                raise GraphQLError(PaymentError.PAYMENT_15)
                        if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES\
                            and not Promotion.objects.filter(
                                id = promotion.promotion_id,
                                valid_from__lte = now,
                                valid_to__gte = now,
                                apply_scope__in = [PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES]
                            ).exists():
                                error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                                raise GraphQLError(PaymentError.PAYMENT_15)
                elif user.isBuyer():
                    if not all(
                        Promotion.objects.filter(
                            id = promotion.promotion_id,
                            valid_from__lte = now,
                            valid_to__gte = now,
                            apply_scope = PromotionApplyScope.FOR_BUYER
                        ).exists() for promotion in wallet.promotion_list
                    ):
                        error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                        raise GraphQLError(PaymentError.PAYMENT_15)

            if wallet.type == 1:
                if user.isSupplier():
                    supplier = Supplier.objects.filter(user=user).first()
                    amount_profile_features = 0
                    amount_sicp_registration = 0

                    if wallet.profile_features is not None and wallet.sicp_registration is not None:
                        if supplier.profile_features_id != int(wallet.profile_features):
                            profile_features = ProfileFeaturesSupplier.objects.filter(id=wallet.profile_features).first()                            
                            amount_profile_features = profile_features.base_rate_full_year
                            profile_feature_name = profile_features.name
                            profile_feature_mount = amount_profile_features
                            upgraded_profile = profile_features
                            supplier.valid_from = timezone.now()
                            supplier.valid_to = timezone.now() + timezone.timedelta(days=365)
                            supplier.send_mail_30_day = None
                            supplier.send_mail_15_day = None
                            supplier.send_mail_7_day = None
                            supplier.send_mail_expire = None
                            if wallet.promotion_list:
                                for promotion in wallet.promotion_list:
                                    if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES:
                                        promotion = Promotion.objects.get(id = promotion.promotion_id)
                                        amount_profile_features = round(amount_profile_features - (amount_profile_features * promotion.discount) / 100)

                        if supplier.sicp_registration_id != int(wallet.sicp_registration):
                            sicp_registration = SICPRegistration.objects.filter(id=wallet.sicp_registration).first()                           
                            amount_sicp_registration = sicp_registration.total_amount
                            sicp_email = sicp_registration
                            sicp_name = sicp_registration.name
                            sicp_amount = amount_sicp_registration
                            if wallet.promotion_list:
                                for promotion in wallet.promotion_list:
                                    if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_SICP:
                                        promotion = Promotion.objects.get(id = promotion.promotion_id)
                                        amount_sicp_registration = round(amount_sicp_registration - (amount_sicp_registration * promotion.discount) / 100)

                        if supplier.profile_features_id == int(wallet.profile_features)\
                            and supplier.sicp_registration_id == int(
                                wallet.sicp_registration
                            ):
                            error = Error(code="PAYMENT_02", message=PaymentError.PAYMENT_02)
                            raise GraphQLError("You must upgrade profile features or sicp registration ")

                        supplier.profile_features_id = wallet.profile_features
                        supplier.sicp_registration_id = wallet.sicp_registration
                        promotion = None
                        discount = 0

                        amount_payment = amount_profile_features + amount_sicp_registration
                        if wallet.promotion is not None:
                            promotion = wallet.promotion
                            promotion_intansce = Promotion.objects.get(id=promotion)
                            if promotion_intansce.status == False:
                                error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                                raise GraphQLError('Promotion code has been deactivated ')
                            discount = promotion_intansce.discount
                            discount_promotion = discount
                            discountContent = promotion_intansce.description

                        supplier.promotion_id = promotion

                        supplier.save()

                        real_amount = round(amount_payment + amount_payment * 0.1)
                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        # vat
                        amount_payment = round(amount_payment * 1.1)

                        history = History.objects.create(
                            order_no=order_no,
                            user_payment=user_payment,
                            type=1,
                            transaction_description="Upgrade Profile",
                            balance=amount_payment,
                            status=2,
                            notes=wallet.notes,
                            method_payment=1,
                            amount=amount_payment,
                        )
                        if promotion_intansce is not None:
                            promotion_user = PromotionUserUsed.objects.create(
                                promotion=promotion_intansce,
                                user_used=user.username,
                                user_used_email=user.email,
                                user_name=user.supplier.company_full_name,
                                title=history.transaction_description,
                                date_used=history.date,
                                real_amount=real_amount,
                                amount_after_discount=history.amount,
                            )
                            if profile_feature_name is not None and sicp_name is not None:
                                profile_name = profile_feature_name + ' and ' + sicp_name
                            elif profile_feature_name is not None:
                                profile_name = profile_feature_name
                            elif sicp_name is not None:
                                profile_name = sicp_name

                            if promotion_intansce.commission is not None and promotion_intansce.user_given_email is not None:
                                profile_amount = profile_feature_mount + sicp_amount                                
                                commission_amount = profile_amount * promotion_intansce.commission / 100                 
                                send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)
                        # bank_transfer
                        if wallet.method_payment == 1:
                            if user_payment.bank_transfer < amount_payment:
                                error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                                raise GraphQLError('Your account do not have enough money')
                            user_payment.bank_transfer = user_payment.bank_transfer - amount_payment
                        # one_pay
                        elif wallet.method_payment == 2:
                            if user_payment.one_pay < amount_payment:
                                error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                                raise GraphQLError('Your account do not have enough money')
                            user_payment.one_pay = user_payment.one_pay - amount_payment

                        else:
                            raise GraphQLError("Method payment  does not exist")

                    diamond_sponsor = UserDiamondSponsor.objects.filter(id=wallet.diamond_sponsor).first()
                    diamond_sponsor_fee = UserDiamondSponsorFee.objects.all().first()
                    if diamond_sponsor is not None:
                        if UserDiamondSponsorPayment.objects.filter(user_diamond_sponsor=diamond_sponsor).exists():
                            error = Error(code="PAYMENT_13", message=PaymentError.PAYMENT_13)
                            raise GraphQLError("The diamond spnosor has been paid")
                        discount=0
                        amount_payment = diamond_sponsor_fee.fee
                        if wallet.promotion is not None:
                            promotion = wallet.promotion
                            promotion_intansce = Promotion.objects.get(id=promotion)                            
                            if promotion_intansce.status == False:
                                error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                                raise GraphQLError('Promotion code has been deactivated ')
                            discount = promotion_intansce.discount

                        real_amount = round(amount_payment + amount_payment * 0.1)
                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        # vat
                        amount_payment = round(amount_payment + amount_payment * 0.1)
                        
                        history = History.objects.create(
                            user_payment=user_payment,
                            type=1,
                            transaction_description="DiamondSponsor",
                            balance=amount_payment,
                            status=2,
                            method_payment=1,
                            notes=wallet.notes,
                            order_no=order_no,
                            amount=amount_payment,
                        )

                        diamond_sponsor_payment = UserDiamondSponsorPayment.objects.create(
                            user_diamond_sponsor=diamond_sponsor,
                            charge_amount=diamond_sponsor_fee.fee,
                            history=history,
                            method_payment=1,
                        )
                        if promotion_intansce is not None:
                            promotion_user = PromotionUserUsed.objects.create(
                                promotion=promotion_intansce,
                                user_used=user.username,
                                user_used_email=user.email,
                                user_name=user.supplier.company_full_name,
                                title=history.transaction_description,
                                date_used=history.date,
                                real_amount=real_amount,
                                amount_after_discount=history.amount,
                            )
                        # bank_transfer
                        if wallet.method_payment == 1:
                            if user_payment.bank_transfer < diamond_sponsor_fee.fee:
                                error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                                raise GraphQLError('Your account do not have enough money')
                            user_payment.bank_transfer = user_payment.bank_transfer - diamond_sponsor_fee.fee
                        # one_pay
                        elif wallet.method_payment == 2:
                            if user_payment.one_pay < diamond_sponsor_fee.fee:
                                error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                                raise GraphQLError('Your account do not have enough money')
                            user_payment.one_pay = user_payment.one_pay - diamond_sponsor_fee.fee
                        else:
                            raise GraphQLError("Method payment  does not exist")

                elif user.isBuyer():
                    buyer = Buyer.objects.filter(user=user).first()
                    if buyer.profile_features_id == int(wallet.profile_features):
                        error = Error(code="PAYMENT_04", message=PaymentError.PAYMENT_04)
                        raise GraphQLError("You must upgrade profile features")

                    profile_features = ProfileFeaturesBuyer.objects.filter(id=wallet.profile_features).first()                        
                    amount_profile_features = profile_features.total_fee_year
                    upgraded_profile = profile_features
                    profile_feature_name = profile_features.name
                    profile_feature_mount = amount_profile_features


                    if wallet.promotion_list:
                        for promotion in wallet.promotion_list:
                            promotion = Promotion.objects.get(id = promotion.promotion_id)
                            amount_profile_features = round(amount_profile_features* (100 - promotion.discount) / 100)
                    promotion = None
                    discount = 0
                    amount_payment = amount_profile_features
                    if wallet.promotion is not None:
                        promotion = wallet.promotion
                        promotion_intansce = Promotion.objects.get(id=promotion)
                        if promotion_intansce.status == False:
                            error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                            raise GraphQLError('Promotion code has been deactivated ')
                        discount = promotion_intansce.discount
                        discount_promotion = discount
                        discountContent = promotion_intansce.description

                    buyer.promotion_id = promotion
                    buyer.profile_features_id = wallet.profile_features
                    buyer.valid_from = timezone.now()
                    buyer.valid_to = timezone.now() + timezone.timedelta(days=365)
                    buyer.send_mail_30_day = None
                    buyer.send_mail_15_day = None
                    buyer.send_mail_7_day = None
                    buyer.send_mail_expire = None
                    buyer.save()

                    real_amount = round(amount_payment + amount_payment * 0.1)
                    amount_payment = amount_payment - (amount_payment * discount) / 100
                    # vat
                    amount_payment = round(amount_payment + amount_payment * 0.1)

                    history = History.objects.create(
                        order_no=order_no,
                        user_payment=user_payment,
                        type=1,
                        transaction_description="Upgrade Profile",
                        balance=amount_payment,
                        status=2,
                        notes=wallet.notes,
                        method_payment=1,
                        amount=amount_payment,
                    )
                    if promotion_intansce is not None:
                        promotion_user = PromotionUserUsed.objects.create(
                            promotion=promotion_intansce,
                            user_used=user.username,
                            user_used_email=user.email,
                            user_name=user.buyer.company_full_name,
                            title=history.transaction_description,
                            date_used=history.date,
                            real_amount=real_amount,
                            amount_after_discount=history.amount,
                        )

                        if promotion_intansce.commission is not None and promotion_intansce.user_given_email is not None:
                            profile_name = profile_feature_name
                            profile_amount = profile_feature_mount
                            commission_amount = profile_amount * promotion_intansce.commission / 100                  
                            send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)
                        
                    if wallet.method_payment == 1:
                        if user_payment.bank_transfer < amount_payment:
                            error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                            raise GraphQLError('Your account do not have enough money')
                        user_payment.bank_transfer = user_payment.bank_transfer - amount_payment
                    elif wallet.method_payment == 2:
                        if user_payment.one_pay < amount_payment:
                            error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                            raise GraphQLError('Your account do not have enough money')
                        user_payment.one_pay = user_payment.one_pay - amount_payment
                    else:
                        raise GraphQLError("Method payment  does not exist")
                else:
                    error = Error(code="PAYMENT_05", message=PaymentError.PAYMENT_05)
                    raise GraphQLError("You must be buyer or supplier")
            if upgraded_profile is not None:
                send_mail_upgraded(user, upgraded_profile)
            if sicp_email is not None:
                send_mail_sicp(user, sicp_email)
            send_mail_paid_successfully(user, history)
            user_payment.save()
            status = True
            return WalletPayment(status=status, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return WalletPayment(error=error, status=False)


class WalletDeposit(graphene.Mutation):
    class Arguments:
        history_id = graphene.String(required=True)
        method_payment = graphene.Int(required=True)
        notes = graphene.String()

    status = graphene.Boolean()
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    def mutate(root, info, history_id, method_payment, notes=None):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            user_payment = UserPayment.objects.filter(user=user).first()
            history = History.objects.filter(id=history_id).first()
            auction_supplier = AuctionSupplier.objects.filter(auction=history.payment_auction.auction, user=user).first()
            if history.status not in (1, 6) or auction_supplier.supplier_status in (2, 4) or auction_supplier.supplier_status != 1:
                error = Error(code="PAYMENT_07", message=PaymentError.PAYMENT_07)
                raise GraphQLError('The transaction is done')

            if history.status == 6 and history.is_parent == True:
                order_no = History.objects.filter().count() + 1
                order_no = '70' + str(order_no).zfill(4)
                payment_auction = PaymentAuction.objects.filter(history=history).first()
                history_intansce = History.objects.create(
                    user_payment=user_payment,
                    type=2,
                    transaction_description=f'''Deposit {payment_auction.auction.item_code}''',
                    balance=history.amount,
                    status=2,
                    method_payment=1,
                    order_no=order_no,
                    amount=history.amount,
                    admin_balance=history.admin_balance,
                    is_parent=True,
                )
                PaymentAuction.objects.create(
                    auction=payment_auction.auction,
                    charge_amount=payment_auction.charge_amount,
                    refund_amount=payment_auction.refund_amount,
                    history=history_intansce,
                    wallet_type=method_payment,
                )
                send_mail_paid_successfully(user, history_intansce)
                history.status = 10
                history.save()
                history = history_intansce

            else:
                history.method_payment = 1
                history.status = 2
                history.balance = history.amount
                history.save()
                send_mail_paid_successfully(user, history)
            auction_supplier.supplier_status = 5
            auction_supplier.save()
            history.payment_auction.refund_amount = history.amount - history.payment_auction.charge_amount
            # bank_transfer
            if method_payment == 1:
                history.payment_auction.wallet_type = 1
                if user_payment.bank_transfer < history.amount:
                    error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                    raise GraphQLError('Your account do not have enough money')
                user_payment.bank_transfer = user_payment.bank_transfer - history.amount
            # one_pay
            elif method_payment == 2:
                history.payment_auction.wallet_type = 2
                if user_payment.one_pay < history.amount:
                    error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                    raise GraphQLError('Your account do not have enough money')
                user_payment.one_pay = user_payment.one_pay - history.amount
            else:
                raise GraphQLError("Method payment  does not exist")
            history.payment_auction.save()
            user_payment.save()
            status = True
            return WalletDeposit(status=status, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return WalletDeposit(error=error, status=False)


class HistoryUpdateStatusInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    status = graphene.Int(required=True)
    notes = graphene.String()


class HistoryUpdateStatus(graphene.Mutation):
    status = graphene.Boolean()
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    class Arguments:
        history = HistoryUpdateStatusInput(required=True)

    def mutate(root, info, history):
        try:
            error = None
            if GetToken.getToken(info).user.isAdmin():
                history_instance = History.objects.filter(id=history.id).first()
                user_payment = history_instance.user_payment

                profile_name = None
                profile_feature_name = None
                sicp_name = None
                profile_amount = 0
                profile_feature_mount = 0
                sicp_amount = 0

                # topup
                if history.status == 2 and history_instance.type == 3 and history_instance.status == 1 and history_instance.method_payment == 2:
                    user_payment.bank_transfer = user_payment.bank_transfer + history_instance.balance
                    history_instance.status = 2
                    send_mail_paid_successfully(user_payment.user, history_instance)

                # payment
                elif (
                    history.status == 2
                    and history_instance.type == 1
                    and history_instance.status == 1
                    and history_instance.bank_transfer_history.is_pending == False
                    and history_instance.method_payment == 2
                ):
                    user = user_payment.user
                    bank_transfer_history = BankTransferHistory.objects.filter(history=history_instance).first()
                    promotion = bank_transfer_history.promotion
                    products = []
                    discount_promotion = None
                    discountContent = None
                    amount_profile_features = 0
                    amount_sicp_registration = 0                    
                    if user.isBuyer():
                        if bank_transfer_history.profile_features_buyer is not None:
                            user.buyer.profile_features = bank_transfer_history.profile_features_buyer
                            user.buyer.valid_from = timezone.now()
                            user.buyer.valid_to = timezone.now() + timezone.timedelta(days=365)
                            user.buyer.send_mail_30_day = None
                            user.buyer.send_mail_15_day = None
                            user.buyer.send_mail_7_day = None
                            user.buyer.send_mail_expire = None
                            user.buyer.save()
                            send_mail_upgraded(user, user.buyer.profile_features)
                            amount_profile_features = user.buyer.profile_features.total_fee_year
                            profile_feature_name = user.buyer.profile_features.name
                            profile_feature_mount = amount_profile_features
                            products.append(
                                {
                                    "code": user.buyer.profile_features.id,
                                    "name": 'Profile Features',
                                    "promotion": False,
                                    "unitPrice": amount_profile_features,
                                    "quantity": 1,
                                    "unit": None,
                                    "currencyUnit": "VND",
                                    "taxRateId": 4,
                                    "extraFields": [],
                                    "subTotal": amount_profile_features,
                                    "hidePrice": False,
                                }
                            )
                            if promotion is not None:
                                promotion_user = PromotionUserUsed.objects.create(
                                    promotion=promotion,
                                    user_used=user.username,
                                    user_used_email=user.email,
                                    user_name=user.buyer.company_full_name,
                                    title=history_instance.transaction_description,
                                    date_used=history_instance.date,
                                    real_amount=history_instance.balance,
                                    amount_after_discount=history_instance.amount,
                                )
                                if promotion.commission is not None and promotion.user_given_email is not None:
                                    profile_name = profile_feature_name
                                    profile_amount = profile_feature_mount
                                    commission_amount = profile_amount * promotion.commission / 100                  
                                    send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)

                    if user.isSupplier():
                        if bank_transfer_history.profile_features_supplier is not None:
                            if user.supplier.profile_features != bank_transfer_history.profile_features_supplier:
                                user.supplier.profile_features = bank_transfer_history.profile_features_supplier
                                user.supplier.send_mail_30_day = None
                                user.supplier.send_mail_15_day = None
                                user.supplier.send_mail_7_day = None
                                user.supplier.send_mail_expire = None
                                user.supplier.valid_from = timezone.now()
                                user.supplier.valid_to = timezone.now() + timezone.timedelta(days=365)
                                send_mail_upgraded(user, bank_transfer_history.profile_features_supplier)
                                amount_profile_features = user.supplier.profile_features.base_rate_full_year
                                profile_feature_name = user.supplier.profile_features.name
                                profile_feature_mount = amount_profile_features
                                products.append(
                                    {
                                        "code": user.supplier.profile_features.id,
                                        "name": 'Profile Features',
                                        "promotion": False,
                                        "unitPrice": amount_profile_features,
                                        "quantity": 1,
                                        "unit": None,
                                        "currencyUnit": "VND",
                                        "taxRateId": 4,
                                        "extraFields": [],
                                        "subTotal": amount_profile_features,
                                        "hidePrice": False,
                                    }
                                )
                        if bank_transfer_history.sicp_registration is not None:
                            if user.supplier.sicp_registration != bank_transfer_history.sicp_registration:
                                user.supplier.sicp_registration = bank_transfer_history.sicp_registration
                                send_mail_sicp(user, bank_transfer_history.sicp_registration)
                                amount_sicp_registration = user.supplier.sicp_registration.total_amount
                                sicp_name = user.supplier.sicp_registration.name
                                sicp_amount = amount_sicp_registration
                                products.append(
                                    {
                                        "code": user.supplier.profile_features.id,
                                        "name": 'Sicp Registration',
                                        "promotion": False,
                                        "unitPrice": amount_sicp_registration,
                                        "quantity": 1,
                                        "unit": None,
                                        "currencyUnit": "VND",
                                        "taxRateId": 4,
                                        "extraFields": [],
                                        "subTotal": amount_sicp_registration,
                                        "hidePrice": False,
                                    }
                                )
                        if promotion is not None:
                            promotion_user = PromotionUserUsed.objects.create(
                                promotion=promotion,
                                user_used=user.username,
                                user_used_email=user.email,
                                user_name=user.supplier.company_full_name,
                                title=history_instance.transaction_description,
                                date_used=history_instance.date,
                                real_amount=history_instance.balance,
                                amount_after_discount=history_instance.amount,
                            )
                            if profile_feature_name is not None and sicp_name is not None:
                                profile_name = profile_feature_name + ' and ' + sicp_name
                            elif profile_feature_name is not None:
                                profile_name = profile_feature_name
                            elif sicp_name is not None:
                                profile_name = sicp_name

                            if promotion.commission is not None and promotion.user_given_email is not None:
                                profile_amount = profile_feature_mount + sicp_amount
                                commission_amount = profile_amount * promotion.commission / 100                  
                                send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)
                        user.supplier.save()
                    if promotion is not None:
                        amount_discount = round((amount_sicp_registration + amount_profile_features) * promotion.discount / 100)
                        discount_promotion = promotion.discount
                        discountContent = promotion.description

                    # refund
                    if history_instance.admin_balance is not None:
                        user_payment.bank_transfer = user_payment.bank_transfer + history_instance.admin_balance
                    history_instance.status = 2
                    send_mail_paid_successfully(user_payment.user, history_instance)
                    data = {
                        "history": history_instance,
                        "user": user,
                        "type": history_instance.method_payment,
                        "product": products,
                        "discount": discount_promotion,
                        "discountContent": discountContent,
                    }
                    history_instance.request_draft_invoice = None

                # pending
                elif (
                    history_instance.type == 1
                    and history_instance.status == 1
                    and history_instance.bank_transfer_history.is_pending == True
                    and history.status == 2
                ):
                    list_history = []
                    total_amount = 0
                    products = []
                    discount_promotion = None
                    discountContent = None
                    if history_instance.is_parent:
                        histories_pending = HistoryPending.objects.filter(history=history_instance, history_pending__status=7)
                        history_parent = history_instance
                        total_amount = history_parent.balance
                        list_history.append(history_parent.id)
                    else:
                        history_pending = HistoryPending.objects.filter(history_pending=history_instance).first()
                        history_parent = history_pending.history
                        histories_pending = HistoryPending.objects.filter(history=history_pending.history, history_pending__status=7)
                        total_amount = history_instance.balance
                        list_history.append(history_instance.id)
                        if history_parent.status == 7:
                            total_amount += history_parent.balance
                            list_history.append(history_parent.id)

                    amount = history_parent.amount
                    history_instance.status = 7

                    if history_parent.status == 2 and history.status == 2:
                        total_amount = 0
                        history_instance.status = 2
                        user_payment.bank_transfer = user_payment.bank_transfer + history_instance.balance
                        history_parent.admin_balance = history_parent.admin_balance + history_instance.balance
                        history_parent.save()

                    for history_pending in histories_pending:
                        list_history.append(history_pending.history_pending.id)
                        total_amount += history_pending.history.balance
                    if amount <= total_amount:
                        history_instance.status = 2
                        history_parent.status = 2
                        History.objects.filter(id__in=list_history).update(status=2, request_draft_invoice=None)
                        user = user_payment.user
                        bank_transfer_history = BankTransferHistory.objects.filter(history=history_parent).first()
                        promotion = bank_transfer_history.promotion
                        amount_profile_features = 0
                        amount_sicp_registration = 0
                        if user.isBuyer():
                            if bank_transfer_history.profile_features_buyer is not None:
                                user.buyer.profile_features = bank_transfer_history.profile_features_buyer
                                user.buyer.valid_from = timezone.now()
                                user.buyer.valid_to = timezone.now() + timezone.timedelta(days=365)
                                user.buyer.send_mail_30_day = None
                                user.buyer.send_mail_15_day = None
                                user.buyer.send_mail_7_day = None
                                user.buyer.send_mail_expire = None
                                user.buyer.save()
                                send_mail_upgraded(user, user.buyer.profile_features)
                                amount_profile_features = user.buyer.profile_features.total_fee_year
                                profile_feature_name = user.buyer.profile_features.name
                                profile_feature_mount = amount_profile_features
                                products.append(
                                    {
                                        "code": user.buyer.profile_features.id,
                                        "name": 'Profile Features',
                                        "promotion": False,
                                        "unitPrice": amount_profile_features,
                                        "quantity": 1,
                                        "unit": None,
                                        "currencyUnit": "VND",
                                        "taxRateId": 4,
                                        "extraFields": [],
                                        "subTotal": amount_profile_features,
                                        "hidePrice": False,
                                    }
                                )

                                if promotion is not None:
                                    promotion_user = PromotionUserUsed.objects.create(
                                        promotion=promotion,
                                        user_used=user.username,
                                        user_used_email=user.email,
                                        user_name=user.buyer.company_full_name,
                                        title=history_instance.transaction_description,
                                        date_used=history_instance.date,
                                        real_amount=history_instance.balance,
                                        amount_after_discount=history_instance.amount,
                                    )
                                    if promotion.commission is not None and promotion.user_given_email is not None:
                                        profile_name = profile_feature_name
                                        profile_amount = profile_feature_mount
                                        commission_amount = profile_amount * promotion.commission / 100                  
                                        send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)

                        if user.isSupplier():
                            if bank_transfer_history.profile_features_supplier is not None:
                                if user.supplier.profile_features != bank_transfer_history.profile_features_supplier:
                                    user.supplier.profile_features = bank_transfer_history.profile_features_supplier
                                    user.supplier.send_mail_30_day = None
                                    user.supplier.send_mail_15_day = None
                                    user.supplier.send_mail_7_day = None
                                    user.supplier.send_mail_expire = None
                                    user.supplier.valid_from = timezone.now()
                                    user.supplier.valid_to = timezone.now() + timezone.timedelta(days=365)
                                    send_mail_upgraded(user, bank_transfer_history.profile_features_supplier)
                                    amount_profile_features = user.supplier.profile_features.base_rate_full_year
                                    profile_feature_name = user.supplier.profile_features.name
                                    profile_feature_mount = amount_profile_features
                                    products.append(
                                        {
                                            "code": user.supplier.profile_features.id,
                                            "name": 'Profile Features',
                                            "promotion": False,
                                            "unitPrice": amount_profile_features,
                                            "quantity": 1,
                                            "unit": None,
                                            "currencyUnit": "VND",
                                            "taxRateId": 4,
                                            "extraFields": [],
                                            "subTotal": amount_profile_features,
                                            "hidePrice": False,
                                        }
                                    )
                            if bank_transfer_history.sicp_registration is not None:
                                if user.supplier.sicp_registration != bank_transfer_history.sicp_registration:
                                    user.supplier.sicp_registration = bank_transfer_history.sicp_registration
                                    send_mail_sicp(user, bank_transfer_history.sicp_registration)
                                    amount_sicp_registration = user.supplier.sicp_registration.total_amount
                                    sicp_name = user.supplier.sicp_registration.name
                                    sicp_amount = amount_sicp_registration
                                    products.append(
                                        {
                                            "code": user.supplier.sicp_registration.id,
                                            "name": 'Sicp Registration',
                                            "promotion": False,
                                            "unitPrice": amount_sicp_registration,
                                            "quantity": 1,
                                            "unit": None,
                                            "currencyUnit": "VND",
                                            "taxRateId": 4,
                                            "extraFields": [],
                                            "subTotal": amount_sicp_registration,
                                            "hidePrice": False,
                                        }
                                    )
                            if promotion is not None:
                                promotion_user = PromotionUserUsed.objects.create(
                                    promotion=promotion,
                                    user_used=user.username,
                                    user_used_email=user.email,
                                    user_name=user.supplier.company_full_name,
                                    title=history_instance.transaction_description,
                                    date_used=history_instance.date,
                                    real_amount=history_instance.balance,
                                    amount_after_discount=history_instance.amount,
                                )
                                if profile_feature_name is not None and sicp_name is not None:
                                    profile_name = profile_feature_name + ' and ' + sicp_name
                                elif profile_feature_name is not None:
                                    profile_name = profile_feature_name
                                elif sicp_name is not None:
                                    profile_name = sicp_name

                                if promotion.commission is not None and promotion.user_given_email is not None:
                                    profile_amount = profile_feature_mount + sicp_amount
                                    commission_amount = profile_amount * promotion.commission / 100                  
                                    send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)
                            user.supplier.save()
                        if promotion is not None:
                            amount_discount = round((amount_sicp_registration + amount_profile_features) * promotion.discount / 100)
                            discount_promotion = promotion.discount
                            discountContent = promotion.description
                        # refund to my account
                        admin_balance = total_amount - amount
                        if admin_balance > 0:
                            user_payment.bank_transfer = user_payment.bank_transfer + admin_balance
                            history_instance.admin_balance += admin_balance
                            history_instance.save()
                        # e-invoice
                        data = {
                            "history": history_parent,
                            "user": user_payment.user,
                            "type": history_parent.method_payment,
                            "product": products,
                            "discount": discount_promotion,
                            "discountContent": discountContent,
                        }
                        history_parent.request_draft_invoice = None
                        history_instance.request_draft_invoice = None
                        history_parent.save()

                    send_mail_paid_successfully(user_payment.user, history_instance)

                elif history.status == 6:
                    if history_instance.type == 4 and history_instance.status == 4 and history_instance.method_payment in (2, 3):
                        history_instance.status = 6
                        if history_instance.method_payment == 2:
                            user_payment.bank_transfer = user_payment.bank_transfer + history_instance.balance
                        else:
                            user_payment.one_pay = user_payment.one_pay + history_instance.balance
                    history_instance.status = 6

                # refund
                elif (
                    history_instance.status == 4 and history.status == 2 and history_instance.type == 4 and history_instance.method_payment in (2, 3)
                ):
                    history_instance.status = 5
                    send_mail_paid_successfully(user_payment.user, history_instance)

                else:
                    raise GraphQLError("error")

                history_instance.save()
                user_payment.save()

                return HistoryUpdateStatus(status=True, history=history_instance)
            raise GraphQLError("No permission")
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return HistoryUpdateStatus(error=error, status=False)


class HistoryUpdateDeposit(graphene.Mutation):
    status = graphene.Boolean()
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    class Arguments:
        history = HistoryUpdateStatusInput(required=True)

    def mutate(root, info, history):
        try:
            error = None
            if GetToken.getToken(info).user.isAdmin():
                history_instance = History.objects.filter(id=history.id).first()
                user_payment = history_instance.user_payment
                if history_instance.is_parent:
                    history_parent = history_instance
                else:
                    history_pending = HistoryPending.objects.filter(history_pending=history_instance).first()
                    history_parent = history_pending.history

                payment_auction = PaymentAuction.objects.filter(history=history_parent).order_by('-id').first()
                auction_supplier = AuctionSupplier.objects.filter(auction=payment_auction.auction, user=user_payment.user).first()
                # comfirm
                if history_instance.status == 1 and history.status == 2 and history_instance.type == 2:

                    total_amount = 0
                    if history_instance.is_parent:
                        histories_pending = HistoryPending.objects.filter(history=history_instance, history_pending__status=2)
                        history_parent = history_instance
                        total_amount = history_parent.balance
                    else:
                        histories_pending = HistoryPending.objects.filter(history=history_pending.history, history_pending__status=2)
                        total_amount = history_instance.balance
                        if history_parent.status == 2:
                            total_amount += history_parent.balance

                    for history_pending in histories_pending:
                        total_amount += history_pending.history.balance

                    if total_amount >= history_parent.amount:
                        admin_balance = total_amount - history_parent.amount
                        user_payment.bank_transfer = user_payment.bank_transfer + admin_balance
                        history_parent.admin_balance = admin_balance
                        history_parent.save()
                        history_parent.payment_auction.refund_amount = history_parent.amount - history_parent.payment_auction.charge_amount
                        history_parent.payment_auction.save()
                        auction_supplier.supplier_status = 5
                    else:
                        auction_supplier.supplier_status = 4
                    history_instance.status = 2
                    history_instance.request_draft_invoice = None
                    send_mail_paid_successfully(user_payment.user, history_instance)

                # paid
                elif auction_supplier.supplier_status == 2 and history_instance.status == 1:
                    total_amount = 0
                    history_instance.status = 2
                    user_payment.bank_transfer = user_payment.bank_transfer + history_instance.balance
                    history_parent.admin_balance += history_instance.balance
                    history_parent.request_draft_invoice = None
                    history_parent.save()
                    send_mail_paid_successfully(user_payment.user, history_instance)

                # cancel
                elif history_instance.status == 1 and history.status == 6:
                    history_instance.status = 6

                # accept deposit
                elif (
                    history_instance.type == 2
                    and auction_supplier.supplier_status in (2, 4)
                    and history.status == 5
                    and history_instance.method_payment == 2
                ):
                    total_amount = 0
                    if history_instance.is_parent:
                        histories_pending = HistoryPending.objects.filter(history=history_instance, history_pending__status=2)
                        history_parent = history_instance
                        total_amount = history_parent.balance
                    else:
                        histories_pending = HistoryPending.objects.filter(history=history_pending.history, history_pending__status=2)
                        total_amount = history_instance.balance
                        if history_parent.status == 2:
                            total_amount += history_parent.balance
                    for history_pending in histories_pending:
                        total_amount += history_pending.history.balance

                    history_parent.payment_auction.refund_amount = (
                        min(history_instance.amount, total_amount) - history_parent.payment_auction.charge_amount
                    )
                    history_parent.payment_auction.save()
                    auction_supplier.supplier_status = 5
                # refuse
                elif history_instance.type == 2 and auction_supplier.supplier_status in (2, 4) and history.status == 7:
                    history_instance.status = 6
                    auction_supplier.supplier_status = 7

                # Refunded
                elif history_instance.type == 2 and auction_supplier.supplier_status == 9 and history.status == 10 and history_instance.status == 3:
                    auction_supplier.supplier_status = 10
                    histories_pending_list = list(
                        map(lambda x: x.get('history_pending'), HistoryPending.objects.filter(history=history_parent).values('history_pending'))
                    )
                    histories_pending_list.append(history_parent.id)
                    histories_pending = History.objects.filter(id__in=histories_pending_list, status=3)
                    amount_bank_transfer = 0
                    check_amount = True
                    for history_pending in histories_pending:
                        amount_bank_transfer += history_pending.balance
                    if amount_bank_transfer < payment_auction.charge_amount:
                        check_amount = False

                    amount_deposit = 0
                    if auction_supplier.awarded == 1:
                        history_instance.status = 9
                        histories_pending.update(status=9)
                    else:
                        history_instance.status = 8
                        histories_pending.update(status=8)
                    if history_instance.method_payment == 2 and check_amount:
                        user_payment.bank_transfer = user_payment.bank_transfer + payment_auction.refund_amount
                    if history_instance.method_payment == 3:
                        user_payment.one_pay = user_payment.one_pay + payment_auction.refund_amount

                    if payment_auction.wallet_type is not None and history_instance.method_payment == 1:
                        # bank_transfer
                        if payment_auction.wallet_type == 1:
                            user_payment.bank_transfer = user_payment.bank_transfer + payment_auction.refund_amount
                        # one_pay
                        elif payment_auction.wallet_type == 2:
                            user_payment.one_pay = user_payment.one_pay + payment_auction.refund_amount
                    if check_amount:
                        history_parent.admin_balance += payment_auction.refund_amount
                        history_parent.save()

                else:
                    raise GraphQLError("error")
                auction_supplier.save()
                user_payment.save()
                history_instance.save()
                return HistoryUpdateDeposit(status=True, history=history_instance)
            raise GraphQLError("No permission")
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return HistoryUpdateDeposit(error=error, status=False)


class RefundRequestInput(graphene.InputObjectType):
    auction_id = graphene.Int(required=True)
    status = graphene.Int(required=True)


class RefundRequest(graphene.Mutation):
    status = graphene.Boolean()
    auction_supplier = graphene.Field(AuctionSupplierNode)
    error = graphene.Field(Error)

    class Arguments:
        input = RefundRequestInput(required=True)

    def mutate(root, info, input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            if user.isSupplier():
                auction_supplier = AuctionSupplier.objects.filter(auction_id=input.auction_id, user=user).first()
                if auction_supplier.supplier_status == 8 and input.status == 9:
                    auction_supplier.supplier_status = 9
                    email_template = EmailTemplates.objects.filter(item_code='RefundRequestSubmitted').first()
                    messages = Template(email_template.translated.content).render(
                        Context(
                            {
                                "image": "https://api.nextpro.io/static/logo_mail.png",
                                "name": user.full_name,
                            }
                        )
                    )
                    try:
                        send_mail(
                            email_template.translated.title,
                            messages,
                            "NextPro <no-reply@nextpro.io>",
                            [user.email],
                            html_message=messages,
                            fail_silently=True,
                        )
                    except:
                        print("fail mail")

                else:
                    raise GraphQLError("error")
                auction_supplier.save()
                return RefundRequest(status=True, auction_supplier=auction_supplier)

            else:
                error = Error(code="PAYMENT_09", message=PaymentError.PAYMENT_09)
                raise GraphQLError("You must be supplier")
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return RefundRequest(error=error, status=False)


# refun banktransfer
class RefundInput(graphene.InputObjectType):
    bank_account_number = graphene.String(required=True)
    bank = graphene.String(required=True)
    amount = graphene.Float(required=True)


class BankTransferRefunds(graphene.Mutation):
    status = graphene.Boolean()
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    class Arguments:
        input = RefundInput(required=True)

    def mutate(root, info, input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            bank_transfers_top_up = BankTransfer.objects.filter(
                user=user, bank_transfer__history__status=2, bank_transfer__history__type=3, bank_transfer__history__method_payment=2
            )
            bank_transfer_payment = BankTransfer.objects.filter(
                user=user,
                bank_transfer__history__status__in=[2, 3, 4, 5, 8, 9],
                bank_transfer__history__type__in=[1, 2],
                bank_transfer__history__method_payment=2,
            )
            amount = 0
            bank = Bank.objects.filter(id=input.bank).first()
            if not BankTransfer.objects.filter(bank=bank, bank_account_number=input.bank_account_number, user=user).exists():
                error = Error(code="PAYMENT_10", message=PaymentError.PAYMENT_10)
                raise GraphQLError("Invalid bank account information")

            user_payment = UserPayment.objects.filter(user=user).first()

            for bank_transfer in bank_transfers_top_up:
                if bank_transfer.bank_account_number == input.bank_account_number and bank_transfer.bank.item_code == bank.item_code:
                    amount += bank_transfer.amount
            for bank_transfer in bank_transfer_payment:
                if bank_transfer.bank_account_number == input.bank_account_number and bank_transfer.bank.item_code == bank.item_code:
                    bank_transfer_history = BankTransferHistory.objects.filter(bank_transfer=bank_transfer).first()
                    amount += bank_transfer_history.history.admin_balance

            amount_refunded = 0
            histories_refunded = History.objects.filter(
                user_payment=user.user_payment,
                status__in=[4, 5],
                type=4,
                method_payment=2,
                bank_transfer_refund__bank=bank,
                bank_transfer_refund__bank_account_number=input.bank_account_number,
            )
            for history_refunded in histories_refunded:
                amount_refunded += history_refunded.balance

            amount = amount - amount_refunded
            if input.amount > amount or input.amount > user_payment.bank_transfer:
                error = Error(code="PAYMENT_11", message=PaymentError.PAYMENT_11)
                raise GraphQLError("Invalid amount")

            order_no = History.objects.filter().count() + 1
            order_no = '70' + str(order_no).zfill(4)
            history = History.objects.create(
                order_no=order_no,
                user_payment=user_payment,
                type=4,
                transaction_description="Refund",
                balance=input.amount,
                status=4,
                method_payment=2,
                amount=None,
            )
            BankTransferRefund.objects.create(history=history, amount=input.amount, bank_account_number=input.bank_account_number, bank=bank)
            user_payment.bank_transfer = user_payment.bank_transfer - history.balance
            user_payment.save()
            return BankTransferRefunds(status=True, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return BankTransferRefunds(error=error, status=False)


# onepay
class OnePayPaymentInput(graphene.InputObjectType):
    type = graphene.Int(required=True)
    profile_features = graphene.String()
    sicp_registration = graphene.String()
    promotion = graphene.String()
    amount = graphene.Float(required=True)
    method_payment = graphene.Int(required=True)
    diamond_sponsor = graphene.String()
    promotion_list = graphene.List(PromotionWalletInput)
    order = graphene.String()

class OnePayCreate(graphene.Mutation):
    status = graphene.Boolean(default_value=False)
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    class Arguments:
        payment = OnePayPaymentInput(required=True)

    def mutate(root, info, payment):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            user_payment = UserPayment.objects.filter(user=user).first()
            detail = []
            is_topup = False
            total = 0
            data = {}
            order_no = History.objects.filter().count() + 1
            order_no = '70' + str(order_no).zfill(4)
            amount_discount = None
            # payment
            if payment.method_payment != 3:
                error = Error(code="PAYMENT_12", message=PaymentError.PAYMENT_12)
                raise GraphQLError("Invalid method payment")
            
            if payment.type == 1:
                promotion = None
                promotion_intansce = None
                if payment.promotion is not None:
                    promotion = payment.promotion
                    promotion_intansce = Promotion.objects.filter(id=promotion).first()
                    if promotion_intansce is None:
                        error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                        raise GraphQLError('Promotion code has been deactivated ')

                    if promotion_intansce.status == False:
                        error = Error(code="PAYMENT_03", message=PaymentError.PAYMENT_03)
                        raise GraphQLError('Promotion code has been deactivated ')
                now = timezone.now()
                if payment.promotion_list:
                    if user.isSupplier():
                        for promotion in payment.promotion_list:
                            if promotion.promotion_type is None:
                                error = Error(code="PAYMENT_17", message=PaymentError.PAYMENT_17)
                                raise GraphQLError(PaymentError.PAYMENT_17)
                            if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_SICP \
                                and not Promotion.objects.filter(
                                    id = promotion.promotion_id,
                                    valid_from__lte = now,
                                    valid_to__gte = now,
                                    apply_scope__in = [PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_SICP]
                                ).exists():
                                    error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                                    raise GraphQLError(PaymentError.PAYMENT_15)
                            if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES\
                                and not Promotion.objects.filter(
                                    id = promotion.promotion_id,
                                    valid_from__lte = now,
                                    valid_to__gte = now,
                                    apply_scope__in = [PromotionApplyScope.FOR_SUPPLIER_ALL_SCOPE, PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES]
                                ).exists():
                                    error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                                    raise GraphQLError(PaymentError.PAYMENT_15)
                    elif user.isBuyer():
                        if not all(
                            Promotion.objects.filter(
                                id = promotion.promotion_id,
                                valid_from__lte = now,
                                valid_to__gte = now,
                                apply_scope = PromotionApplyScope.FOR_BUYER
                            ).exists() for promotion in payment.promotion_list
                        ):
                            error = Error(code="PAYMENT_15", message=PaymentError.PAYMENT_15)
                            raise GraphQLError(PaymentError.PAYMENT_15)

            if payment.type == 1:
                if user.isSupplier():
                    supplier = Supplier.objects.filter(user=user).first()
                    amount_profile_features = 0
                    amount_sicp_registration = 0
                    profile_features = supplier.profile_features
                    sicp_registration = supplier.sicp_registration

                    if payment.profile_features is not None and payment.sicp_registration is not None:
                        profile_features_id = int(payment.profile_features)
                        sicp_registration_id = int(payment.sicp_registration)

                        if HistoryOnePay.objects.filter(
                            profile_features_supplier_id=profile_features_id,
                            sicp_registration_id=sicp_registration_id,
                            history__status=7,
                            history__user_payment=user_payment,
                        ).exists():
                            error = Error(code="PAYMENT_01", message=PaymentError.PAYMENT_01)
                            raise GraphQLError("The transaction is waiting for the administrator to confirm")

                        if supplier.profile_features_id != profile_features_id:
                            profile_features = ProfileFeaturesSupplier.objects.filter(id=profile_features_id).first()
                            amount_profile_features = profile_features.base_rate_full_year
                            if payment.promotion_list:
                                for promotion in payment.promotion_list:
                                    if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES:
                                        promotion = Promotion.objects.get(id = promotion.promotion_id)
                                        amount_profile_features = round(amount_profile_features - (amount_profile_features * promotion.discount) / 100)

                        if supplier.sicp_registration_id != sicp_registration_id:
                            sicp_registration = SICPRegistration.objects.filter(id=sicp_registration_id).first()
                            amount_sicp_registration = sicp_registration.total_amount
                            if payment.promotion_list:
                                for promotion in payment.promotion_list:
                                    if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_SICP:
                                        promotion = Promotion.objects.get(id = promotion.promotion_id)
                                        amount_sicp_registration = round(amount_sicp_registration - (amount_sicp_registration * promotion.discount) / 100)

                        if supplier.sicp_registration_id == sicp_registration_id and supplier.profile_features_id == profile_features_id:
                            error = Error(code="PAYMENT_02", message=PaymentError.PAYMENT_02)
                            raise GraphQLError("You must upgrade profile features or sicp registration ")

                        discount = 0
                        amount_payment = amount_profile_features + amount_sicp_registration
                        if payment.promotion is not None:
                            discount = promotion_intansce.discount

                        supplier.promotion_id = promotion
                        supplier.save()
                        if payment.promotion_list:
                            for promotion in payment.promotion_list:
                                if promotion.promotion_type == PromotionApplyScope.FOR_SUPPLIER_PROFILE_FEATURES:
                                    promotion = Promotion.objects.get(id = promotion.promotion_id)
                                    amount_profile_features = round(amount_profile_features - (amount_profile_features * promotion.discount) / 100)
                        
                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)
                        if amount_payment != payment.amount:
                            error = Error(code="PAYMENT_11", message=PaymentError.PAYMENT_11)
                            raise GraphQLError("Invalid amount")

                        history = History.objects.create(
                            user_payment=user_payment,
                            type=1,
                            transaction_description="Upgrade Profile",
                            balance=payment.amount,
                            status=7,
                            method_payment=3,
                            order_no=order_no,
                            amount=amount_payment,
                        )
                        history_one_pay = HistoryOnePay.objects.create(
                            history=history, profile_features_supplier=profile_features, sicp_registration=sicp_registration, promotion_id=promotion
                        )

                    diamond_sponsor = UserDiamondSponsor.objects.filter(id=payment.diamond_sponsor).first()
                    diamond_sponsor_fee = UserDiamondSponsorFee.objects.all().first()
                    if diamond_sponsor is not None:
                        if diamond_sponsor_fee.fee >= payment.amount:
                            error = Error(code="PAYMENT_11", message=PaymentError.PAYMENT_11)
                            raise GraphQLError("Invalid amount")

                        if UserDiamondSponsorPayment.objects.filter(user_diamond_sponsor=diamond_sponsor).exists():
                            error = Error(code="PAYMENT_13", message=PaymentError.PAYMENT_13)
                            raise GraphQLError("The diamond spnosor has been paid")

                        discount = 0
                        amount_payment = diamond_sponsor_fee.fee
                        if payment.promotion is not None:
                            discount = promotion_intansce.discount

                        supplier.promotion_id = promotion
                        supplier.save()

                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)

                        history = History.objects.create(
                            user_payment=user_payment,
                            type=1,
                            transaction_description="DiamondSponsor",
                            balance=payment.amount,
                            status=7,
                            method_payment=3,
                            order_no=order_no,
                            amount=amount_payment,
                        )

                        history_one_pay = HistoryOnePay.objects.create(
                            history=history,
                            diamond_sponsor=diamond_sponsor,
                            promotion_id=promotion,
                        )

                        diamond_sponsor_payment = UserDiamondSponsorPayment.objects.create(
                            user_diamond_sponsor=diamond_sponsor,
                            charge_amount=payment.amount,
                            history=history,
                            method_payment=payment.method_payment,
                        )

                    if payment.order is not None:
                        order = Order.objects.filter(order_id = payment.order).first()
                        if order is None:
                            error = Error(code="PAYMENT_21", message=PaymentError.PAYMENT_21)
                            raise GraphQLError("This order does not exists.")
                        discount = 0
                        amount_payment = order.amount
                        if payment.promotion is not None:
                            discount = promotion_intansce.discount

                        supplier.promotion_id = promotion
                        supplier.save()

                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)

                        history = History.objects.create(
                            user_payment=user_payment,
                            type=1,
                            transaction_description="Order",
                            balance=payment.amount,
                            status=7,
                            method_payment=3,
                            order_no=order_no,
                            amount=amount_payment,
                        )

                        history_one_pay = HistoryOnePay.objects.create(
                            history=history,
                            diamond_sponsor=diamond_sponsor,
                            promotion_id=promotion,
                        )

                        order.order_status = OrderStatus.PAID.value
                        order.save()

                elif user.isBuyer():
                    discount = 0
                    buyer = Buyer.objects.filter(user=user).first()
                    profile_features_id = int(payment.profile_features)

                    if HistoryOnePay.objects.filter(
                        profile_features_buyer_id=profile_features_id,
                        history__status=1,
                        history__user_payment=user_payment,
                    ).exists():
                        error = Error(code="PAYMENT_01", message=PaymentError.PAYMENT_01)
                        raise GraphQLError("The transaction is waiting for the administrator to confirm")

                    if payment.order is not None:
                        order = Order.objects.filter(order_id = payment.order).first()
                        if order is None:
                            error = Error(code="PAYMENT_21", message=PaymentError.PAYMENT_21)
                            raise GraphQLError("This order does not exists.")
                        amount_payment = order.amount
                        if payment.promotion is not None:
                            discount = promotion_intansce.discount

                        buyer.promotion_id = promotion
                        buyer.save()
                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)
                        if amount_payment != payment.amount:
                            error = Error(code="PAYMENT_11", message=PaymentError.PAYMENT_11)
                            raise GraphQLError("Invalid amount")
                        history = History.objects.create(
                            user_payment=user_payment,
                            type=1,
                            transaction_description="Order",
                            balance=payment.amount,
                            status=7,
                            method_payment=3,
                            order_no=order_no,
                            amount=amount_payment,
                        )
                        history_one_pay = HistoryOnePay.objects.create(history=history, profile_features_buyer=profile_features, promotion_id=promotion)
                        order.order_status = OrderStatus.PAID.value
                        order.save()
                    else:
                        if buyer.profile_features_id != profile_features_id:
                            profile_features = ProfileFeaturesBuyer.objects.filter(id=profile_features_id).first()
                            amount_profile_features = profile_features.total_fee_year
                        else:
                            error = Error(code="PAYMENT_04", message=PaymentError.PAYMENT_04)
                            raise GraphQLError("You must upgrade profile features")
                        if payment.promotion_list:
                            for promotion in payment.promotion_list:
                                promotion = Promotion.objects.get(id = promotion.promotion_id)
                                amount_profile_features = round(amount_profile_features* (100 - promotion.discount) / 100)
                        
                        amount_payment = amount_profile_features
                        if payment.promotion is not None:
                            discount = promotion_intansce.discount

                        buyer.promotion_id = promotion
                        buyer.save()
                        amount_payment = amount_payment - (amount_payment * discount) / 100
                        sub_total = round(amount_payment)
                        amount_payment = round(amount_payment + amount_payment * 0.1)
                        if amount_payment != payment.amount:
                            error = Error(code="PAYMENT_11", message=PaymentError.PAYMENT_11)
                            raise GraphQLError("Invalid amount")
                        history = History.objects.create(
                            user_payment=user_payment,
                            type=1,
                            transaction_description="Upgrade Profile",
                            balance=payment.amount,
                            status=7,
                            method_payment=3,
                            order_no=order_no,
                            amount=amount_payment,
                        )
                        history_one_pay = HistoryOnePay.objects.create(history=history, profile_features_buyer=profile_features, promotion_id=promotion)
                else:
                    error = Error(code="PAYMENT_05", message=PaymentError.PAYMENT_05)
                    raise GraphQLError("You must be buyer or supplier")
            # Topup
            elif payment.type == 3:
                history = History.objects.create(
                    user_payment=user_payment,
                    type=3,
                    transaction_description="Topup",
                    balance=payment.amount,
                    status=7,
                    method_payment=3,
                    order_no=order_no,
                )
                history_one_pay = HistoryOnePay.objects.create(history=history)
                sub_total = payment.amount
                is_topup = True

            else:
                raise GraphQLError("Type does not exists ")
            history.save()
            return OnePayCreate(status=True, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return OnePayCreate(error=error, status=False)

class UserDiamondSponsorPaymentFilter(FilterSet):
    class Meta:
        model = UserDiamondSponsorPayment
        fields =  {
            'id': ['exact'],
            'charge_amount': ['exact'],
            'method_payment': ['exact']
            }

    order_by = OrderingFilter(fields=('id', 'charge_amount','method_payment'))

class UserDiamondSponsorPaymentNode(DjangoObjectType):
    class Meta:
        model = UserDiamondSponsorPayment
        filterset_class = UserDiamondSponsorPaymentFilter
        interfaces = (CustomNode,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

class OnePayDeposit(graphene.Mutation):
    status = graphene.Boolean(default_value=True)
    history = graphene.Field(HistoryNode)
    error = graphene.Field(Error)

    class Arguments:
        history_id = graphene.String(required=True)
        amount = graphene.Float(required=True)
        method_payment = graphene.Int(required=True)

    def mutate(root, info, history_id, amount, method_payment):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            user_payment = UserPayment.objects.filter(user=user).first()
            history = History.objects.filter(id=history_id).first()
            history_parent = history
            if history.is_parent == False:
                history_pending = HistoryPending.objects.filter(history_pending=history).first()
                history_parent = history_pending.history
            auction_supplier = AuctionSupplier.objects.filter(auction=history_parent.payment_auction.auction, user=user).first()

            if method_payment != 3:
                error = Error(code="PAYMENT_12", message=PaymentError.PAYMENT_12)
                raise GraphQLError("Invalid method payment")
            if history.status not in (1, 6) or auction_supplier.supplier_status not in [1]:
                error = Error(code="PAYMENT_07", message=PaymentError.PAYMENT_07)
                raise GraphQLError('The transaction is done')

            if history.status == 6:

                order_no = History.objects.filter().count() + 1
                order_no = '70' + str(order_no).zfill(4)
                history_intansce = History.objects.create(
                    user_payment=user_payment,
                    type=2,
                    transaction_description=history.transaction_description,
                    status=7,
                    order_no=order_no,
                    balance=history.balance,
                    amount=history.amount,
                    is_parent=True,
                    method_payment=3,
                    admin_balance=history.admin_balance,
                )
                HistoryOnePay.objects.create(history=history_intansce)
                payment_auction = PaymentAuction.objects.filter(history=history).first()
                PaymentAuction.objects.create(
                    auction=payment_auction.auction,
                    charge_amount=payment_auction.charge_amount,
                    refund_amount=payment_auction.refund_amount,
                    history=history_intansce,
                )
                history.status = 10
                history.save()
                history = history_intansce

            else:
                history.balance = amount
                history.status = 7
                history.payment_auction.refund_amount = history.amount - history.payment_auction.charge_amount
                history.payment_auction.save()
                # Deposited
                if history.amount != amount:
                    error = Error(code="PAYMENT_11", message=PaymentError.PAYMENT_11)
                    raise GraphQLError("Invalid amount")

                detail = [
                    {
                        'description': f'''Deposit {history.payment_auction.auction.item_code}''',
                        'quantity': 1,
                        'unit_price': history.amount,
                        'total_amount': history.amount,
                    }
                ]

                history_one_pay = HistoryOnePay.objects.create(history=history)
                sub_total = round(history.amount - history.amount * 0.1)
                data = {
                    'user': user,
                    'invoice_no': history.order_no,
                    'invoice_date': datetime.strftime(history.date, '%d-%m-%Y'),
                    'detail_list': detail,
                    'sub_total': sub_total,
                    'is_topup': False,
                }
                history.method_payment = 3
                history.save()
            return OnePayDeposit(status=True, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return OnePayDeposit(error=error, status=False)


class OnePayRefund(graphene.Mutation):
    history = graphene.Field(HistoryNode)
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Arguments:
        amount = graphene.Float(required=True)

    def mutate(root, info, amount):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="PAYMENT_06", message=PaymentError.PAYMENT_06)
            user_payment = UserPayment.objects.filter(user=user).first()
            if user_payment.one_pay < amount:
                error = Error(code="PAYMENT_08", message=PaymentError.PAYMENT_08)
                raise GraphQLError('Your account do not have enough money')
            order_no = History.objects.filter().count() + 1
            order_no = '70' + str(order_no).zfill(4)
            history = History.objects.create(
                order_no=order_no,
                user_payment=user_payment,
                type=4,
                transaction_description="Refund",
                balance=amount,
                status=4,
                method_payment=3,
                amount=None,
            )
            user_payment.one_pay = user_payment.one_pay - history.balance
            user_payment.save()
            return OnePayRefund(history=history, status=True)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return OnePayRefund(error=error, status=False)


class OnePayUpdateStatus(graphene.Mutation):
    history = graphene.Field(HistoryNode)
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Arguments:
        history = HistoryUpdateStatusInput(required=True)

    def mutate(root, info, history):
        try:
            profile_name = None
            profile_feature_name = None
            sicp_name = None
            profile_amount = 0
            profile_feature_mount = 0
            sicp_amount = 0

            history_instance = History.objects.filter(id=history.id).first()
            history_one_pay = HistoryOnePay.objects.filter(history=history_instance).first()
            history_parent = history_instance
            if history_instance.is_parent == False:
                history_pending = HistoryPending.objects.filter(history_pending=history_instance).first()
                history_parent = history_pending.history

            user_payment = history_instance.user_payment
            if history.status == 2 and history_instance.type == 3 and history_instance.status in (7, 2) and history_instance.method_payment == 3:
                if history_instance.status == 7:
                    user_payment.one_pay = user_payment.one_pay + history_instance.balance
                    send_mail_paid_successfully(user_payment.user, history_instance)
                history_instance.status = 2
            elif history.status == 2 and history_instance.type == 1 and history_instance.status in (7, 2) and history_instance.method_payment == 3:
                user = user_payment.user
                if history_instance.status == 7:
                    promotion = history_one_pay.promotion
                    amount_sicp_registration = 0
                    amount_profile_features = 0
                    products = []
                    discount_promotion = None
                    discountContent = None
                    if user.isBuyer():
                        if history_one_pay.profile_features_buyer is not None:
                            user.buyer.profile_features = history_one_pay.profile_features_buyer
                            user.buyer.valid_from = timezone.now()
                            user.buyer.valid_to = timezone.now() + timezone.timedelta(days=365)
                            user.buyer.send_mail_30_day = None
                            user.buyer.send_mail_15_day = None
                            user.buyer.send_mail_7_day = None
                            user.buyer.send_mail_expire = None
                            user.buyer.save()
                            send_mail_upgraded(user, user.buyer.profile_features)
                            amount_profile_features = user.buyer.profile_features.total_fee_year
                            products.append(
                                {
                                    "code": user.buyer.profile_features.id,
                                    "name": 'Profile Features',
                                    "promotion": False,
                                    "unitPrice": amount_profile_features,
                                    "quantity": 1,
                                    "unit": None,
                                    "currencyUnit": "VND",
                                    "taxRateId": 4,
                                    "extraFields": [],
                                    "subTotal": amount_profile_features,
                                    "hidePrice": False,
                                }
                            )
                            profile_feature_name = history_one_pay.profile_features_buyer.name
                            profile_feature_mount = amount_profile_features
                            if promotion is not None:
                                promotion_user = PromotionUserUsed.objects.create(
                                    promotion=promotion,
                                    user_used=user.username,
                                    user_used_email=user.email,
                                    user_name=user.buyer.company_full_name,
                                    title=history_instance.transaction_description,
                                    date_used=history_instance.date,
                                    real_amount=history_instance.balance,
                                    amount_after_discount=history_instance.amount,
                                )

                                if promotion.commission is not None and promotion.user_given_email is not None:
                                    profile_name = profile_feature_name
                                    profile_amount = profile_feature_mount
                                    commission_amount = profile_amount * promotion.commission / 100                  
                                    send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)
                                
                    if user.isSupplier():
                        if history_one_pay.profile_features_supplier is not None or history_one_pay.sicp_registration is not None:
                            if user.supplier.profile_features != history_one_pay.profile_features_supplier:
                                user.supplier.profile_features = history_one_pay.profile_features_supplier
                                send_mail_upgraded(user, history_one_pay.profile_features_supplier)
                                user.supplier.send_mail_30_day = None
                                user.supplier.send_mail_15_day = None
                                user.supplier.send_mail_7_day = None
                                user.supplier.send_mail_expire = None
                                user.supplier.valid_from = timezone.now()
                                user.supplier.valid_to = timezone.now() + timezone.timedelta(days=365)
                                amount_profile_features = user.supplier.profile_features.base_rate_full_year
                                profile_feature_name = history_one_pay.profile_features_supplier.name
                                profile_feature_mount = amount_profile_features
                                products.append(
                                    {
                                        "code": user.supplier.profile_features.id,
                                        "name": 'Profile Features',
                                        "promotion": False,
                                        "unitPrice": amount_profile_features,
                                        "quantity": 1,
                                        "unit": None,
                                        "currencyUnit": "VND",
                                        "taxRateId": 4,
                                        "extraFields": [],
                                        "subTotal": amount_profile_features,
                                        "hidePrice": False,
                                    }
                                )

                            if user.supplier.sicp_registration != history_one_pay.sicp_registration:
                                user.supplier.sicp_registration = history_one_pay.sicp_registration
                                send_mail_sicp(user, history_one_pay.sicp_registration)
                                amount_sicp_registration = user.supplier.sicp_registration.total_amount
                                sicp_name = user.supplier.sicp_registration.name
                                sicp_amount = amount_sicp_registration.total_amount
                                products.append(
                                    {
                                        "code": user.supplier.sicp_registration.id,
                                        "name": 'Sicp Registration',
                                        "promotion": False,
                                        "unitPrice": amount_sicp_registration,
                                        "quantity": 1,
                                        "unit": None,
                                        "currencyUnit": "VND",
                                        "taxRateId": 4,
                                        "extraFields": [],
                                        "subTotal": amount_sicp_registration,
                                        "hidePrice": False,
                                    }
                                )

                            if promotion is not None:
                                promotion_user = PromotionUserUsed.objects.create(
                                    promotion=promotion,
                                    user_used=user.username,
                                    user_used_email=user.email,
                                    user_name=user.supplier.company_full_name,
                                    title=history_instance.transaction_description,
                                    date_used=history_instance.date,
                                    real_amount=history_instance.balance,
                                    amount_after_discount=history_instance.amount,
                                )
                                if profile_feature_name is not None and sicp_name is not None:
                                    profile_name = profile_feature_name + ' and ' + sicp_name
                                elif profile_feature_name is not None:
                                    profile_name = profile_feature_name
                                elif sicp_name is not None:
                                    profile_name = sicp_name

                                if promotion.commission is not None and promotion.user_given_email is not None:
                                    profile_amount = profile_feature_mount + sicp_amount
                                    commission_amount = profile_amount * promotion.commission / 100                  
                                    send_mail_promotion(promotion_user, user, profile_name, profile_amount, commission_amount)
                            user.supplier.save()
                    if promotion is not None:
                        amount_discount = round((amount_sicp_registration + amount_profile_features) * promotion.discount / 100)
                        discount_promotion = promotion.discount
                        discountContent = promotion.description
                    # e-invoice
                    data = {
                        "history": history_instance,
                        "user": user,
                        "type": history_instance.method_payment,
                        "product": products,
                        "discount": discount_promotion,
                        "discountContent": discountContent,
                    }
                    send_mail_paid_successfully(user_payment.user, history_instance)
                history_instance.status = 2

            elif history.status == 2 and history_instance.type == 2 and history_instance.status in (2, 7) and history_instance.method_payment == 3:
                if history_instance.status == 7:
                    payment_auction = PaymentAuction.objects.filter(history=history_parent).order_by('-id').first()
                    auction_supplier = AuctionSupplier.objects.filter(auction=payment_auction.auction, user=user_payment.user).first()
                    auction_supplier.supplier_status = 5
                    auction_supplier.save()
                    send_mail_paid_successfully(user_payment.user, history_instance)
                history_instance.status = 2
            elif history.status == 6:
                history_instance.status = 6
            else:
                raise GraphQLError("errors")
            history_one_pay.notes = history.notes
            history_one_pay.save()
            user_payment.save()
            history_instance.save()

            return OnePayUpdateStatus(history=history_instance, status=True)
        except Exception as err:
            transaction.set_rollback(True)
            return OnePayUpdateStatus(err, status=False)


class Query(ObjectType):

    user_payment = CustomNode.Field(UserPaymentNode)
    user_payments = CustomizeFilterConnectionField(UserPaymentNode)

    bank_transfer = CustomNode.Field(BankTransferNode)
    bank_transfers = CustomizeFilterConnectionField(BankTransferNode)
    bank_transfer_history = CustomNode.Field(BankTransferHistoryNode)
    bank_transfer_histories = CustomizeFilterConnectionField(BankTransferHistoryNode)

    history_payment = CustomNode.Field(HistoryNode)
    history_payments = CustomizeFilterConnectionField(HistoryNode)

    history_pending = CustomNode.Field(HistoryPendingNode)
    histories_pending = CustomizeFilterConnectionField(HistoryPendingNode)

    bank_transfer_accounts = graphene.List(BankTransferAccount)

    user_diamond_sponsor_payment = CustomNode.Field(UserDiamondSponsorPaymentNode)
    user_diamond_sponsor_payments = CustomizeFilterConnectionField(UserDiamondSponsorPaymentNode)

    def resolve_bank_transfer_accounts(root, info):
        user = GetToken.getToken(info).user
        result = []
        bank_transfers = BankTransfer.objects.filter(user=user).distinct("bank", "bank_account_number")
        bank_transfers_top_up = BankTransfer.objects.filter(
            user=user, bank_transfer__history__status=2, bank_transfer__history__type=3, bank_transfer__history__method_payment=2
        )
        bank_transfers_payment = BankTransfer.objects.filter(
            user=user,
            bank_transfer__history__status__in=[2, 3, 4, 5, 8, 9],
            bank_transfer__history__type__in=[1, 2],
            bank_transfer__history__method_payment=2,
        )
        user_payment = UserPayment.objects.filter(user=user).first()
        for bank_transfer in bank_transfers:
            bank_info = {}
            bank_info['bank'] = bank_transfer.bank
            bank_info['bank_number'] = bank_transfer.bank_account_number
            amount = 0
            for bank_transfer_top_up in bank_transfers_top_up:
                if (
                    bank_transfer_top_up.bank_account_number == bank_transfer.bank_account_number
                    and bank_transfer_top_up.bank.item_code == bank_transfer.bank.item_code
                ):
                    amount += bank_transfer_top_up.amount
            for bank_transfer_payment in bank_transfers_payment:
                if (
                    bank_transfer_payment.bank_account_number == bank_transfer.bank_account_number
                    and bank_transfer_payment.bank.item_code == bank_transfer.bank.item_code
                ):
                    bank_transfer_history = BankTransferHistory.objects.filter(bank_transfer=bank_transfer_payment).first()
                    if bank_transfer_history.history.admin_balance is not None:
                        amount += bank_transfer_history.history.admin_balance
            amount_refunded = 0

            histories_refunded = History.objects.filter(
                user_payment=user.user_payment,
                status__in=[4, 5],
                type=4,
                method_payment=2,
                bank_transfer_refund__bank=bank_transfer.bank,
                bank_transfer_refund__bank_account_number=bank_transfer.bank_account_number,
            )
            for history_refunded in histories_refunded:
                amount_refunded += history_refunded.balance

            amount = amount - amount_refunded
            bank_info['amount'] = amount
            result.append(bank_info)

        return result


class Mutation(graphene.ObjectType):
    bank_transfer_create = BankTransferCreate.Field()
    bank_transfer_for_zero_create = BankTransferForZeroCreate.Field()
    bank_transfer_pending = BankTransferPending.Field()
    bank_transfer_deposit = BanksTransferDeposit.Field()
    payment_pending_check = PaymentPendingCheck.Field()

    history_update_status = HistoryUpdateStatus.Field()
    history_update_deposit = HistoryUpdateDeposit.Field()

    wallet_payment = WalletPayment.Field()
    wallet_deposit = WalletDeposit.Field()

    refund_request = RefundRequest.Field()
    bank_transfer_refund = BankTransferRefunds.Field()

    one_pay_create = OnePayCreate.Field()
    one_pay_deposit = OnePayDeposit.Field()
    one_pay_refund = OnePayRefund.Field()
    one_pay_update_status = OnePayUpdateStatus.Field()
