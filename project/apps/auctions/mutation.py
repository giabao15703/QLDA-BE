import graphene
import math
import pytz

from apps.auctions.error_code import AuctionError
from apps.auctions.models import (
    Auction,
    AuctionAward,
    AuctionSupplier,
    AuctionBid,
    AuctionItemSupplier,
    AuctionItem,
    AuctionGeneralTermCondition,
    AuctionOtherRequirement,
    AuctionTypeTrafficLight,
    AuctionTypeRanking,
    AuctionTypePrices,
    AuctionTypeSealedBid,
    AuctionTypeDutch,
    AuctionTypeJapanese,
)
from apps.auctions.query import AuctionNode
from apps.core import Error
from apps.invoices.views import invoice_generate
from apps.master_data.models import (
    EmailTemplates,
    Coupon,
    Category,
    Currency,
    ContractType,
    TechnicalWeighting,
    PaymentTerm,
    DeliveryTerm,
    AuctionType,
    UnitofMeasure,
    EmailTemplatesTranslation,
)
from apps.payment.models import History, PaymentAuction, HistoryPending
from apps.payment.schema import HistoryNode
from apps.rfx.models import RFXData, RFXSupplier
from apps.sale_schema.models import AuctionFee, PlatformFee
from apps.users.error_code import UserError
from apps.users.models import User, Buyer, BuyerSubAccounts
from apps.users.schema import GetToken
from datetime import datetime
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Max, Sum
from django.template import Template, Context
from django.utils import timezone
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

def send_mail_award(item_code, supplier_award):
    language_code = supplier_award.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": supplier_award.user.full_name,
                "auction_item_code": supplier_award.auction.item_code,
                "link": "https://auction.nextpro.io/payment/my-account",
            }
        )
    )
    title = Template(email_template.title).render(Context({"auction_item_code": supplier_award.auction.item_code,}))

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [supplier_award.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_coupon_award(auction, total_charge):
    email_template = EmailTemplates.objects.filter(item_code='CouponTransactionAuction').first()
    coupon = Coupon.objects.get(coupon_program=auction.coupon)
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": coupon.full_name,
                "auction_no": auction.item_code,
                'buyer_name': auction.user.full_name,
                'auction_title': auction.title,
                'supplier_charged_amount': "{:10,.2f}".format(total_charge),
            }
        )
    )
    title = Template(email_template.title).render(Context({"code": coupon.coupon_program,}))

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [coupon.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")

def send_mail_canncel_auction_supplier(item_code,supplier,auction,reason):
    language_code = supplier.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": supplier.user.full_name,
                "auction_item_code": auction.item_code,
                "auction_title": auction.title,
                "reason":reason,
                "buyer_company_name":auction.user.buyer.company_full_name,
                "link": "https://auction.nextpro.io/auth/login",
            }
        )
    )
    title = Template(email_template.title).render(Context({"auction_item_code": supplier.auction.item_code,}))

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [supplier.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")

def send_mail_canncel_auction_buyer(item_code,buyer,auction,reason):
    language_code = buyer.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": buyer.user.full_name,
                "auction_item_code": auction.item_code,
                "auction_title": auction.title,
                "reason":reason,
                "link": "https://auction.nextpro.io/payment/my-account",
            }
        )
    )
    title = Template(email_template.title).render(Context({"auction_item_code": auction.item_code,}))

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [buyer.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


class AuctionAwardSupplierInput(graphene.InputObjectType):
    user_id = graphene.String(required=True)
    percentage = graphene.Float(required=True)


class AuctionAwardInput(graphene.InputObjectType):
    auction_item_id = graphene.String(required=True)
    supplier = graphene.List(AuctionAwardSupplierInput, required=True)


class AuctionAwardCreate(graphene.Mutation):

    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        items = graphene.List(AuctionAwardInput)
        auction_id = graphene.String(required=True)
        user_id = graphene.String()

    def mutate(root, info, auction_id, items=None, user_id=None):
        try:
            error = None
            supplier_list = []
            auction = Auction.objects.filter(id=auction_id).first()
            auction_next_round = Auction.objects.filter(auction_next_round=auction).exists()
            platform_fee = PlatformFee.objects.all().first()
            if auction.status != 4 or auction_next_round:
                raise GraphQLError("errors")
            if auction.split_order == 2 and user_id is None:
                for item in items:
                    auction_item = AuctionItem.objects.filter(id=item.auction_item_id).first()

                    total_percent = 0
                    for supplier_award in item.supplier:
                        total_percent += supplier_award.percentage
                        auction_bid = AuctionBid.objects.filter(user_id=supplier_award.user_id, auction_item=auction_item).order_by('id')
                        if auction_item.quantity * supplier_award.percentage % 100 != 0:
                            error = Error(code="AUCTION_25", message=AuctionError.AUCTION_25)
                            raise GraphQLError("Invalid percentage")

                        if auction_bid.exists():
                            price = auction_bid.last().price
                        else:
                            auction_item_supplier = AuctionItemSupplier.objects.filter(
                                auction_item=auction_item, auction_supplier__user_id=supplier_award.user_id, auction_supplier__is_accept=True,
                            ).first()
                            price = auction_item_supplier.confirm_price

                        auction_award = AuctionAward.objects.create(
                            user_id=supplier_award.user_id,
                            auction=auction,
                            auction_item=auction_item,
                            percentage=supplier_award.percentage,
                            price=price,
                            platform_fee=platform_fee.fee,
                        )
                        supplier_list.append(int(supplier_award.user_id))
                    if total_percent != 100:
                        error = Error(code="AUCTION_26", message=AuctionError.AUCTION_26)
                        raise GraphQLError("The total percentage must be 100 percent ")
            elif auction.split_order == 1 or user_id is not None:
                auction_items = AuctionItem.objects.filter(auction=auction)
                for auction_item in auction_items:

                    auction_bid = AuctionBid.objects.filter(user=user_id, auction_item=auction_item).order_by('id')

                    if auction_bid.exists():
                        price = auction_bid.last().price
                    else:
                        auction_item_supplier = AuctionItemSupplier.objects.filter(
                            auction_item=auction_item, auction_supplier__user_id=user_id, auction_supplier__is_accept=True
                        ).first()
                        price = auction_item_supplier.confirm_price

                    auction_award = AuctionAward.objects.create(
                        auction=auction, auction_item=auction_item, user_id=user_id, percentage=100, price=price, platform_fee=platform_fee.fee
                    )
                supplier_list.append(int(user_id))
            AuctionSupplier.objects.filter(supplier_status=6, auction=auction, user_id__in=supplier_list).update(awarded=1, supplier_status=8)
            AuctionSupplier.objects.filter(supplier_status=6, auction=auction).exclude(user_id__in=supplier_list).update(awarded=2, supplier_status=8)
            auction.status = 5
            auction.save()
            supplier_awards = AuctionSupplier.objects.filter(auction=auction, supplier_status=8)
            total_charge = 0
            for supplier_award in supplier_awards:
                amount_deposit = 0
                if supplier_award.awarded == 1:
                    auction_awards = AuctionAward.objects.filter(user=supplier_award.user, auction=auction)
                    for auction_award in auction_awards:
                        amount_deposit += (auction_award.percentage * auction_award.price) / 100
                    send_mail_award("ChargedDeposit", supplier_award)
                elif supplier_award.awarded == 2:
                    send_mail_award("RefundedDepositMyAccount", supplier_award)

                auction_payment = PaymentAuction.objects.filter(
                    auction=auction, history__user_payment__user=supplier_award.user, history__is_parent=True
                ).first()
                history = auction_payment.history
                if amount_deposit > 0:
                    platform_fee = PlatformFee.objects.all().first()
                    amount_usd = amount_deposit
                    auction_fee = AuctionFee.objects.filter(min_value__lte=amount_usd, max_value__gte=amount_usd)
                    auction_fee = auction_fee.first()
                    if auction_fee is None:
                        value = AuctionFee.objects.filter().aggregate(Max('max_value'))
                        auction_fee = AuctionFee.objects.filter(max_value=value.get('max_value__max')).first()
                    amount_deposit = (amount_deposit * auction_fee.percentage) / 100
                    total_charge += amount_deposit

                auction_payment.charge_amount = round(auction_payment.charge_amount + amount_deposit * 1.1)
                auction_payment.refund_amount = round(auction_payment.refund_amount - amount_deposit * 1.1)
                auction_payment.save()
                detail = [
                    {
                        'description': f'''Deposit {auction.item_code}''',
                        'quantity': 1,
                        'unit_price': round(auction_payment.charge_amount / 1.1),
                        'total_amount': round(auction_payment.charge_amount / 1.1),
                    }
                ]
                data = {
                    'user': supplier_award.user,
                    'invoice_no': history.order_no,
                    'invoice_date': datetime.strftime(timezone.now(), '%d-%m-%Y'),
                    'detail_list': detail,
                    'sub_total': round(auction_payment.charge_amount / 1.1),
                    'is_topup': False,
                }
                invoice_generate(data)
                history.request_draft_invoice = f'''{supplier_award.user.id}/{history.order_no}/draft_invoice.pdf'''
                history.save()

                products = [
                    {
                        "code": auction.item_code,
                        "name": f'''Deposit {auction.item_code}''',
                        "unitPrice": round(auction_payment.charge_amount / 1.1),
                        "quantity": 1,
                        "unit": None,
                        "currencyUnit": "VND",
                        "taxRateId": None,
                        "extraFields": [],
                        "subTotal": round(auction_payment.charge_amount / 1.1),
                        "hidePrice": False,
                        "promotion": False,
                    }
                ]
                data_invoice = {
                    "history": history,
                    "user": supplier_award.user,
                    "type": history.method_payment,
                    "product": products,
                    "deposit": auction_payment.charge_amount,
                }

            # Awaiting refunding request
            payment_auctions = PaymentAuction.objects.filter(auction=auction).exclude(history__status=10)
            for payment_auction in payment_auctions:
                histories_pending_list = list(
                    map(lambda x: x.get('history_pending'), HistoryPending.objects.filter(history=payment_auction.history).values('history_pending'))
                )
                histories_pending_list.append(payment_auction.history.id)
                histories_pending = History.objects.filter(id__in=histories_pending_list, status=2).update(status=3)
            # send mail coupon
            if Coupon.objects.filter(coupon_program=auction.coupon).exists():
                send_mail_coupon_award(auction, total_charge)
            return AuctionAwardCreate(status=True)
        except Exception as err:
            print(err)
            transaction.set_rollback(True)
            if error is None:
                error = err
            return AuctionAwardCreate(error=error, status=False)


# --------------------------create auction----------------------------------------
class OptionsInput(graphene.InputObjectType):
    max_price_settings = graphene.Boolean()
    max_price_type = graphene.Int()
    individual_or_max_price = graphene.Int()
    hide_target_price = graphene.Boolean()
    type_of_bidding = graphene.Int()
    type_of_bid_monitoring1 = graphene.Boolean()
    type_of_bid_monitoring2 = graphene.Boolean()
    type_of_bid_monitoring3 = graphene.Boolean()
    type_of_bid_monitoring5 = graphene.Boolean()
    type_of_bid_monitoring6 = graphene.Boolean()
    views_disabled = graphene.Int()
    minutes = graphene.Int()
    auction_extension = graphene.Int()
    auction_extension_trigger = graphene.Float()
    number_of_rankings = graphene.Int()
    frequency = graphene.Int()
    trigger_time = graphene.Int()
    prolongation_by = graphene.Int()
    entire_auction = graphene.Float()
    initial_price = graphene.Float()
    end_price = graphene.Float()
    price_step = graphene.Float()
    price_validity = graphene.Float()
    warning_minutes = graphene.Int()


class ItemSupplierInput(graphene.InputObjectType):
    user = graphene.String(required=True)
    price = graphene.Float(required=True)
    technical_score = graphene.Float()


class ItemInput(graphene.InputObjectType):
    id = graphene.String()
    name = graphene.String(required=True)
    budget = graphene.Float()
    unit = graphene.String(required=True)
    quantity = graphene.Float(required=True)
    price_yellow = graphene.Float()
    target_price = graphene.Float()
    minimum_bid_step = graphene.Float()
    maximum_bid_step = graphene.Float()
    max_price = graphene.Float()
    description = graphene.String()
    suppliers = graphene.List(ItemSupplierInput, required=True)


class AuctionInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    budget = graphene.Float(required=True)
    category = graphene.String(required=True)
    currency = graphene.String(required=True)
    start_time = graphene.DateTime(required=True)
    end_time = graphene.DateTime(required=True)
    contract_type = graphene.String()
    contract_from = graphene.DateTime()
    contract_to = graphene.DateTime()
    delivery_date = graphene.String()
    payment_term = graphene.String()
    delivery_term = graphene.String()
    delivery_address = graphene.String()
    note_from_supplier = graphene.String()
    note_from_buyer = graphene.String()
    technical_weighting = graphene.String(required=True)
    auction_type1 = graphene.String(required=True)
    status = graphene.Int(required=True)
    user = graphene.String(required=True)
    split_order = graphene.Int(required=True)
    auction_next_round = graphene.Int()
    other_requirementss = graphene.List(Upload)
    general_term_conditionss = graphene.List(Upload)
    coupon = graphene.String()
    options = graphene.Field(OptionsInput, required=True)
    auction_items = graphene.List(ItemInput, required=True)
    negotiation_after_obe = graphene.Int(required=True)
    auction_rules = graphene.String()
    general_term_conditions_delete = graphene.List(graphene.Int)
    other_requirements_delete = graphene.List(graphene.Int)
    duplicated_auction_id = graphene.String()
    rfx_id = graphene.String()


class AuctionCreate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    auction = graphene.Field(AuctionNode)

    class Arguments:
        input = AuctionInput(required=True)

    def mutate(root, info, input):
        try:
            error = None
            auction_count = Auction.objects.filter(auction_next_round__isnull=True).count() + 1
            item_code = '60' + str(auction_count).zfill(4)
            if input.auction_next_round:
                auction = Auction.objects.filter(id=input.auction_next_round).first()
                AuctionSupplier.objects.filter(auction_id=input.auction_next_round).exclude(supplier_status=7).update(supplier_status=11)
                item_code = float("{0:.2f}".format(float(auction.item_code) + 0.1))
            input['item_code'] = item_code
            auction = Auction()
            for key, values in input.items():
                if key in [f.name for f in Auction._meta.get_fields()]:
                    if key == "category":
                        values = Category.objects.get(id=values)
                    elif key == "currency":
                        values = Currency.objects.get(id=values)
                    elif key == "contract_type":
                        values = ContractType.objects.get(id=values)
                    elif key == "payment_term":
                        values = PaymentTerm.objects.get(id=values)
                    elif key == "delivery_term":
                        values = DeliveryTerm.objects.get(id=values)
                    elif key == "technical_weighting":
                        values = TechnicalWeighting.objects.get(id=values)
                    elif key == "auction_type1":
                        values = AuctionType.objects.get(id=values)
                    elif key == "user":
                        values = User.objects.get(id=values)
                    elif key == "auction_next_round":
                        values = Auction.objects.get(id=values)

                    setattr(auction, key, values)
            auction.save()
            if input.rfx_id is not None:
                rfx = RFXData.objects.get(id=input.rfx_id)
                rfx.status=5
                rfx.save(update_fields=['status'])
                auction.rfx=rfx
                auction.save(update_fields=['rfx_id'])
                user_ids = []
                for item in input.auction_items:
                    for supplier in item['suppliers']:
                        user_ids.append(supplier['user'])
                RFXSupplier.objects.filter(rfx=rfx, user_id__in=user_ids).update(quote_submited_status=3)
                RFXSupplier.objects.filter(rfx=rfx, quote_submited_status=2).exclude(user_id__in=user_ids).update(quote_submited_status=5)

            if input.duplicated_auction_id:
                auction_copy = Auction.objects.filter(pk=input.duplicated_auction_id).first()
                if input.general_term_conditions_delete is not None:
                    general_term_conditions = AuctionGeneralTermCondition.objects.filter(auction=auction_copy).exclude(
                        id__in=input.general_term_conditions_delete
                    )
                    if input.general_term_conditionss is None:
                        input.general_term_conditionss = []
                    for i in general_term_conditions:
                        input.general_term_conditionss.append(i.general_term_condition)
                if input.other_requirements_delete is not None:
                    other_requirements = AuctionOtherRequirement.objects.filter(auction=auction_copy).exclude(id__in=input.other_requirements_delete)
                    if input.other_requirementss is None:
                        input.other_requirementss = []
                    for i in other_requirements:
                        input.other_requirementss.append(i.other_requirement)
            if input.other_requirementss:
                AuctionOtherRequirement.objects.filter(auction=auction).delete()
                for file in input.other_requirementss:
                    AuctionOtherRequirement.objects.create(auction=auction, other_requirement=file)
            if input.general_term_conditionss:
                AuctionGeneralTermCondition.objects.filter(auction=auction).delete()
                for file in input.general_term_conditionss:
                    AuctionGeneralTermCondition.objects.create(auction=auction, general_term_condition=file)

            suppliers_of_auction = len(input.auction_items[0].suppliers)
            auction_type_data = input.options
            auction_type_data["auction"] = auction

            # -------About-max(starting)-price--------------------------------------
            # -------Setting-max-price-of-Traffic-Light-or-Ranking-or-Prices-are-same-----------------

            if auction.auction_type1_id == 1 or auction.auction_type1_id == 3 or auction.auction_type1_id == 4:
                # --Case: False, Null, Null -----------------------------------
                if auction_type_data.max_price_settings is None or auction_type_data.type_of_bid_monitoring6 is None:
                    error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                    raise GraphQLError("err")

                if auction_type_data.get('max_price_settings') is False:
                    auction_type_data['max_price_type'] = None
                    auction_type_data['individual_or_max_price'] = None
                    auction_type_data['entire_auction'] = None
                elif auction_type_data.get('max_price_settings') is True:
                    if auction_type_data.get('max_price_type') is None:
                        error = Error(code="AUCTION_02", message=AuctionError.AUCTION_02)
                        raise GraphQLError("err")

                    if auction_type_data.get('individual_or_max_price') is None:
                        error = Error(code="AUCTION_03", message=AuctionError.AUCTION_03)
                        raise GraphQLError("Please check individual or maximum price")

                    if auction_type_data.get('max_price_type') == 1 and auction_type_data.get('individual_or_max_price') == 2:
                        if auction_type_data.entire_auction is None:
                            error = Error(code="AUCTION_04", message=AuctionError.AUCTION_04)
                            raise GraphQLError("Please fill max price for entire Auction.")
                        else:
                            pass
                    else:
                        auction_type_data['entire_auction'] = None

            # --------------------------------------------------------------------------------------------------

            if auction.auction_type1_id == 4:  # Prices
                if auction_type_data.auction_extension is None:
                    error = Error(code="AUCTION_05", message=AuctionError.AUCTION_05)

                    raise GraphQLError("You must type the required auction extension field.")

                # Check of bid mornitoring - views disabled and extension--------------------------------------
                if auction_type_data.type_of_bid_monitoring6 is False:
                    auction_type_data['views_disabled'] = None
                    auction_type_data['minutes'] = None
                elif auction_type_data.type_of_bid_monitoring6 is True:
                    if auction_type_data.views_disabled is None:
                        error = Error(code="AUCTION_06", message=AuctionError.AUCTION_06)
                        raise GraphQLError("You must type the  views disabled required field.")
                    if auction_type_data.views_disabled == 1:
                        auction_type_data['minutes'] = None
                        auction_type_data['type_of_bid_monitoring1'] = False

                    if auction_type_data.views_disabled == 2 and auction_type_data.minutes is None:
                        error = Error(code="AUCTION_07", message=AuctionError.AUCTION_07)
                        raise GraphQLError("Please fill the rest time you want to the information of suppliers be disabled.")

                if auction_type_data.auction_extension == 1:
                    if auction_type_data.warning_minutes is None:
                        error = Error(code="AUCTION_24", message=AuctionError.AUCTION_24)
                        raise GraphQLError("You must type the  warning minutes required field.")
                    auction_type_data['auction_extension_trigger'] = None
                    auction_type_data['number_of_rankings'] = None
                    auction_type_data['frequency'] = None
                    auction_type_data['trigger_time'] = None
                    auction_type_data['prolongation_by'] = None
                else:

                    if auction_type_data['type_of_bidding'] == 2:
                        auction_type_data['auction_extension_trigger'] = 1
                        auction_type_data['number_of_rankings'] = None
                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None or auction_type_data.trigger_time is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")
                    if auction_type_data['type_of_bidding'] == 1:
                        if auction_type_data.auction_extension_trigger is None:
                            error = Error(code="AUCTION_08", message=AuctionError.AUCTION_08)
                            raise GraphQLError("You must select the way how to trigger when chosing Automatic extension.")

                        if auction_type_data.auction_extension_trigger == 2:
                            if auction_type_data.number_of_rankings is None:
                                error = Error(code="AUCTION_09", message=AuctionError.AUCTION_09)
                                raise GraphQLError("You must type the number of ranking when chosing the second way trigger.")

                            if auction_type_data.number_of_rankings > suppliers_of_auction:
                                error = Error(code="AUCTION_10", message=AuctionError.AUCTION_10)
                                raise GraphQLError("You must type a number lower than or equal to the number of suppliers.")

                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")

                        if auction_type_data.auction_extension_trigger != 2:
                            auction_type_data['number_of_rankings'] = None

                        if auction_type_data.auction_extension_trigger == 3:
                            auction_type_data['trigger_time'] = None
                        else:
                            if auction_type_data.trigger_time is None:
                                error = Error(code="AUCTION_11", message=AuctionError.AUCTION_11)
                                raise GraphQLError("You must type the required trigger time.")
            # --------------------------------------------------------------------------------------------------

            if auction.auction_type1_id == 1:  # Traffic Light
                # ------Check-case-of-bid-mornitoring----------------------------------------
                # ------Check-3rd-then check-or-not-4th----------------------------------------
                # if auction_type_data['type_of_bid_monitoring3'] is False
                # -------Check-6th-then-disabled-all-rest---------------------------------------

                if auction_type_data.type_of_bid_monitoring6 is False:
                    auction_type_data.views_disabled = None
                    auction_type_data['minutes'] = None
                elif auction_type_data.type_of_bid_monitoring6 is True:
                    if auction_type_data.views_disabled is None:
                        error = Error(code="AUCTION_06", message=AuctionError.AUCTION_06)
                        raise GraphQLError("You must type the required views_disabled.")
                    if auction_type_data.views_disabled == 1:
                        auction_type_data['minutes'] = None
                        auction_type_data['type_of_bid_monitoring1'] = False
                        auction_type_data['type_of_bid_monitoring2'] = False
                        auction_type_data['type_of_bid_monitoring3'] = False

                    if auction_type_data.views_disabled == 2 and auction_type_data.minutes is None:
                        error = Error(code="AUCTION_12", message=AuctionError.AUCTION_12)

                        raise GraphQLError("Please fill the time you want to the information of suppliers be disabled.")
            # Ranking
            if auction.auction_type1_id == 3:
                # ------Check-case-of-bid-mornitoring----------------------------------------
                # ------Check-3rd-then check-or-not-4th----------------------------------------

                # -------Check-6th-then-disabled-all-rest---------------------------------------
                if auction_type_data.type_of_bid_monitoring6 is False:
                    auction_type_data['views_disabled'] = None
                    auction_type_data['minutes'] = None
                elif auction_type_data.type_of_bid_monitoring6 is True:
                    if auction_type_data.views_disabled is None:
                        error = Error(code="AUCTION_06", message=AuctionError.AUCTION_06)
                        raise GraphQLError("You must type the required field(s).")
                    if auction_type_data.views_disabled == 1:
                        auction_type_data['minutes'] = None
                        auction_type_data['type_of_bid_monitoring1'] = False
                        auction_type_data['type_of_bid_monitoring3'] = False

                    if auction_type_data.views_disabled == 2 and auction_type_data.minutes is None:
                        error = Error(code="AUCTION_12", message=AuctionError.AUCTION_12)
                        raise GraphQLError("Please fill the time you want to the information of suppliers be disabled.")

                # -------------------------------------------------------------------------------------------------------------
                # ---------Type of bidding affect directly to extension trigger ------------------------------------------------

                if auction_type_data['type_of_bid_monitoring3'] is False:
                    if auction_type_data['type_of_bidding'] == 2:
                        error = Error(code="AUCTION_13", message=AuctionError.AUCTION_13)

                        raise GraphQLError("Default: Bidder sees the best bid ")

                if auction_type_data['auction_extension'] == 1:
                    if auction_type_data.warning_minutes is None:
                        error = Error(code="AUCTION_24", message=AuctionError.AUCTION_24)
                        raise GraphQLError("You must type the  warning minutes required field.")
                    auction_type_data['auction_extension_trigger'] = None
                    auction_type_data['number_of_rankings'] = None
                    auction_type_data['frequency'] = None
                    auction_type_data['trigger_time'] = None
                    auction_type_data['prolongation_by'] = None
                else:
                    if auction_type_data['type_of_bidding'] == 2:
                        auction_type_data['auction_extension_trigger'] = 1
                        auction_type_data['number_of_rankings'] = None
                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None or auction_type_data.trigger_time is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")
                    if auction_type_data['type_of_bidding'] == 1:
                        if auction_type_data.auction_extension_trigger is None:
                            error = Error(code="AUCTION_08", message=AuctionError.AUCTION_08)
                            raise GraphQLError("You must select the way how to trigger when chosing Automatic extension.")

                        if auction_type_data.auction_extension_trigger == 2:
                            if auction_type_data.number_of_rankings is None:
                                error = Error(code="AUCTION_09", message=AuctionError.AUCTION_09)

                                raise GraphQLError("You must type the number of ranking when chosing the second way trigger.")
                            if auction_type_data.number_of_rankings > suppliers_of_auction:
                                error = Error(code="AUCTION_10", message=AuctionError.AUCTION_10)

                                raise GraphQLError('You must type a number lower than or equal to the number of suppliers.')

                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")

                        if auction_type_data.auction_extension_trigger != 2:
                            auction_type_data['number_of_rankings'] = None

                        if auction_type_data.auction_extension_trigger == 3:
                            auction_type_data['trigger_time'] = None
                        else:
                            if auction_type_data.trigger_time is None:
                                error = Error(code="AUCTION_11", message=AuctionError.AUCTION_11)

                                raise GraphQLError("You must type the required trigger time.")

                # ----------Check condition of Dutch Auction--------------------
            if auction.auction_type1_id == 5:
                if (
                    auction_type_data.initial_price is None
                    or auction_type_data.end_price is None
                    or auction_type_data.price_step is None
                    or auction_type_data.price_validity is None
                ):
                    error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                    raise GraphQLError("You must type the required field(s).")

                if auction_type_data.initial_price >= auction_type_data.end_price:
                    error = Error(code="AUCTION_16", message=AuctionError.AUCTION_16)

                    raise GraphQLError("Initial price must be lower than end price.")

                if (auction_type_data.initial_price + auction_type_data.price_step) > auction_type_data.end_price:
                    error = Error(code="AUCTION_17", message=AuctionError.AUCTION_17)
                    raise GraphQLError("You must type valid price step.")
                round_auction = (auction_type_data.end_price - auction_type_data.initial_price) / auction_type_data.price_step
                round_auction = math.ceil(round_auction) + 1

            # ----------Check condition of Japanese Auction--------------------
            if auction.auction_type1_id == 6:
                if (
                    auction_type_data.initial_price is None
                    or auction_type_data.end_price is None
                    or auction_type_data.price_step is None
                    or auction_type_data.price_validity is None
                ):
                    error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                    raise GraphQLError("You must type the required field(s).")
                if auction_type_data.initial_price <= auction_type_data.end_price:
                    error = Error(code="AUCTION_18", message=AuctionError.AUCTION_18)

                    raise GraphQLError("Initial price must be greater than end price.")
                if (auction_type_data.initial_price - auction_type_data.price_step) < auction_type_data.end_price:
                    error = Error(code="AUCTION_17", message=AuctionError.AUCTION_17)
                    raise GraphQLError("You must type valid price step.")

                round_auction = (auction_type_data.initial_price - auction_type_data.end_price) / auction_type_data.price_step
                round_auction = math.ceil(round_auction) + 1

            if auction.auction_type1_id == 2:
                auction_type_data['type_of_bid_monitoring6'] = True
                auction_type_data['views_disabled'] = 1
                auction_type_data['auction_extension'] = 1

            # save auction type
            if auction.auction_type1_id == 1:  # Traffic Light
                auction_type = AuctionTypeTrafficLight()
                for key, values in auction_type_data.items():
                    if key in [f.name for f in AuctionTypeTrafficLight._meta.get_fields()]:
                        setattr(auction_type, key, values)
            elif auction.auction_type1_id == 2:  # Sealed Bid
                auction_type = AuctionTypeSealedBid()
                for key, values in auction_type_data.items():
                    if key in [f.name for f in AuctionTypeSealedBid._meta.get_fields()]:
                        setattr(auction_type, key, values)
            elif auction.auction_type1_id == 3:  # Ranking
                auction_type = AuctionTypeRanking()
                for key, values in auction_type_data.items():
                    if key in [f.name for f in AuctionTypeRanking._meta.get_fields()]:
                        setattr(auction_type, key, values)
            elif auction.auction_type1_id == 4:  # Prices
                auction_type = AuctionTypePrices()
                for key, values in auction_type_data.items():
                    if key in [f.name for f in AuctionTypePrices._meta.get_fields()]:
                        setattr(auction_type, key, values)
            elif auction.auction_type1_id == 5:
                auction_type = AuctionTypeDutch()
                auction_type_data["round_auction"] = round_auction
                for key, values in auction_type_data.items():
                    if key in [f.name for f in AuctionTypeDutch._meta.get_fields()]:
                        setattr(auction_type, key, values)
            elif auction.auction_type1_id == 6:
                auction_type = AuctionTypeJapanese()
                auction_type_data["round_auction"] = round_auction
                for key, values in auction_type_data.items():
                    if key in [f.name for f in AuctionTypeJapanese._meta.get_fields()]:
                        setattr(auction_type, key, values)
            auction_type.save()

            # ---Case: entire Auction--------Calculate the average of all items and compare to max price of all items----------------
            # ---Case: True, 1, 2---------------------database  updated-------------------------

            if (
                auction.auction_type1_id == 1 or auction.auction_type1_id == 3 or auction.auction_type1_id == 4
            ):  # add this line as Sealed bid dooes not have fields about max price
                if auction_type.max_price_settings is True and auction_type.max_price_type == 1 and auction_type.individual_or_max_price == 2:
                    average_price_total = 0
                    price_item = 0
                    for item in input.auction_items:
                        for supplier in item['suppliers']:
                            price_item = price_item + supplier['price']
                        average_price_total = price_item / len(item['suppliers'])

                    for item in input.auction_items:
                        item['max_price'] = None

                    max_price_all_items = auction_type_data['entire_auction']

                    percent = 0.8
                    bounded_max_price = percent * average_price_total
                    error_max_and_average_total = abs(max_price_all_items - average_price_total)

                    if error_max_and_average_total > bounded_max_price:
                        error = Error(code="AUCTION_19", message=AuctionError.AUCTION_19)
                        raise GraphQLError(
                            "You choose max price for entire Auction. \n Please fill in max price such that value of all items between 0,2 and 1,8 average of all items."
                        )
            # ----------------------------------------------------------------------------
            user_buyer = User.objects.select_related('buyer').get(id=auction.user_id)
            # Start to save items
            for item in input.auction_items:
                auction_item_data = item
                auction_item_data['auction'] = auction
                if auction.auction_type1_id == 1:  # Traffic Light
                    if (
                        auction_item_data.target_price is None
                        or auction_item_data.price_yellow is None
                        or auction_item_data.minimum_bid_step is None
                        or auction_item_data.maximum_bid_step is None
                    ):
                        error = Error(code="AUCTION_20", message=AuctionError.AUCTION_20)
                        raise GraphQLError(
                            " Please check price level for yellow, target price, minimum bid step and maximum bid step, maybe one of these fields be incomplete"
                        )

                    if (
                        auction_type.max_price_settings is True
                        and auction_type.max_price_type == 2
                        and auction_type.individual_or_max_price == 2
                        and auction_item_data.max_price is None
                    ):
                        error = Error(code="AUCTION_21", message=AuctionError.AUCTION_21)

                        raise GraphQLError("Please fill value of max price for all items as chosing setting True")

                    if auction_type.max_price_settings is False:
                        auction_item_data['max_price'] = None

                    if auction_type.individual_or_max_price == 1:
                        auction_item_data['max_price'] = None

                if auction.auction_type1_id == 3 or auction.auction_type1_id == 4:  # Ranking-Prices
                    auction_item_data['price_yellow'] = None

                    if auction_item_data.minimum_bid_step is None or auction_item_data.maximum_bid_step is None:
                        error = Error(code="AUCTION_14", message=AuctionError.AUCTION_14)
                        raise GraphQLError("Please fill in minimum bid step and maximum bid step.")
                    if (
                        auction_type.max_price_settings is True
                        and auction_type.max_price_type == 2
                        and auction_type.individual_or_max_price == 2
                        and auction_item_data.max_price is None
                    ):
                        error = Error(code="AUCTION_21", message=AuctionError.AUCTION_21)
                        raise GraphQLError("Please fill value of max price for all items as chosing setting True")

                    if auction_type.max_price_settings is False:
                        auction_item_data['max_price'] = None

                    if auction_type.individual_or_max_price == 1:
                        auction_item_data['max_price'] = None

                if auction.auction_type1_id == 2 or auction.auction_type1_id == 5 or auction.auction_type1_id == 6:  # Sealed Bid #Dutch #Japanese
                    auction_item_data['price_yellow'] = None
                    auction_item_data['target_price'] = None
                    auction_item_data['minimum_bid_step'] = None
                    auction_item_data['maximum_bid_step'] = None
                    auction_item_data['max_price'] = None

                # ---Case: Per position--------Calculate the average of each item and compare to max price of each item----------------
                # ---Case: True, 2, 2 ------------------------------------------------------------------------
                if (
                    auction.auction_type1_id == 1 or auction.auction_type1_id == 3 or auction.auction_type1_id == 4
                ):  # add this line as Sealed bid dooes not have fields about max price
                    if auction_type.max_price_settings is True and auction_type.max_price_type == 2 and auction_type.individual_or_max_price == 2:
                        price_item = 0
                        for supplier in item['suppliers']:
                            price_item = price_item + supplier['price']

                        average_price_item = price_item / len(item['suppliers'])
                        bounded_max_price = 0.8 * average_price_item
                        error_max_and_start = abs(auction_item_data['max_price'] - average_price_item)

                        if error_max_and_start > bounded_max_price:
                            error = Error(code="AUCTION_15", message=AuctionError.AUCTION_15)
                            raise GraphQLError(
                                "You set max price per position. \n Please fill value of max price not greater or lower than 80 percent average value of suppliers for each item."
                            )
                        else:
                            pass

                auction_item = AuctionItem()
                for key, values in auction_item_data.items():
                    if key in [f.name for f in AuctionItem._meta.get_fields()]:
                        if key == "unit":
                            values = UnitofMeasure.objects.get(id=values)
                        if key != "suppliers":
                            setattr(auction_item, key, values)
                auction_item.save()
                # --------------------------------------------------------------------------
                for supplier in item.suppliers:
                    auction_supplier_data = supplier
                    auction_supplier_data['auction'] = auction
                    auction_supplier_data['supplier_status'] = 1
                    if AuctionSupplier.objects.filter(auction=auction, user_id=supplier['user']).exists():
                        auction_supplier = AuctionSupplier.objects.get(auction_id=auction.id, user_id=supplier['user'])
                    else:
                        auction_supplier = AuctionSupplier()
                        for key, values in auction_supplier_data.items():
                            if key in [f.name for f in AuctionSupplier._meta.get_fields()]:
                                if key == "user":
                                    values = User.objects.get(id=values)
                                setattr(auction_supplier, key, values)
                        auction_supplier.save()

                    auction_item_supplier_data = supplier
                    auction_item_supplier_data["auction"] = auction
                    auction_item_supplier_data["auction_item"] = auction_item
                    auction_item_supplier_data["auction_supplier"] = auction_supplier
                    auction_item_supplier = AuctionItemSupplier()
                    for key, values in auction_item_supplier_data.items():
                        if key in [f.name for f in AuctionItemSupplier._meta.get_fields()]:
                            if key == "user":
                                values = User.objects.get(id=values)
                            setattr(auction_item_supplier, key, values)
                    auction_item_supplier.save()

            # check number auction buyer
            if not check_number_auction_buyer(user=auction.user):
                error = Error(code="AUCTION_22", message=AuctionError.AUCTION_22)
                raise GraphQLError("The number of Auction has exceeded the amount")
            if auction.status == 2:
                # send mail
                send_mail_published_auction(auction=auction)
            if auction.status not in (1, 2):
                error = Error(code="AUCTION_23", message=AuctionError.AUCTION_23)
                raise GraphQLError("Auction status must be 1 or 2")
            return AuctionCreate(auction=auction, status=True)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return AuctionCreate(status=False, error=error)

class AuctionUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    auction = graphene.Field(AuctionNode)

    class Arguments:
        id = graphene.String(required=True)
        input = AuctionInput(required=True)

    def mutate(root, info, input, id):
        try:
            error = None
            auction = Auction.objects.get(id=id)
            for key, values in input.items():
                if key in [f.name for f in Auction._meta.get_fields()]:
                    if key == "category":
                        values = Category.objects.get(id=values)
                    elif key == "currency":
                        values = Currency.objects.get(id=values)
                    elif key == "contract_type":
                        values = ContractType.objects.get(id=values)
                    elif key == "payment_term":
                        values = PaymentTerm.objects.get(id=values)
                    elif key == "delivery_term":
                        values = DeliveryTerm.objects.get(id=values)
                    elif key == "technical_weighting":
                        values = TechnicalWeighting.objects.get(id=values)
                    elif key == "auction_type1":
                        values = AuctionType.objects.get(id=values)
                    elif key == "user":
                        values = User.objects.get(id=values)
                    elif key == "auction_next_round":
                        values = Auction.objects.get(id=values)

                    setattr(auction, key, values)
            auction.save()
            for id in input.general_term_conditions_delete:
                AuctionGeneralTermCondition.objects.filter(id=id).delete()

            for id in input.other_requirements_delete:
                AuctionOtherRequirement.objects.filter(id=id).delete()

            if input.other_requirementss:
                for file in input.other_requirementss:
                    AuctionOtherRequirement.objects.create(auction=auction, other_requirement=file)
            if input.general_term_conditionss:
                for file in input.general_term_conditionss:
                    AuctionGeneralTermCondition.objects.create(auction=auction, general_term_condition=file)

            suppliers_of_auction = len(input.auction_items[0].suppliers)
            auction_type_data = input.options
            auction_type_data["auction"] = auction

            # -------About-max(starting)-price--------------------------------------
            # -------Setting-max-price-of-Traffic-Light-or-Ranking-or-Prices-are-same-----------------

            if auction.auction_type1_id == 1 or auction.auction_type1_id == 3 or auction.auction_type1_id == 4:
                # --Case: False, Null, Null -----------------------------------
                if auction_type_data.max_price_settings is None or auction_type_data.type_of_bid_monitoring6 is None:
                    error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                    raise GraphQLError("err")

                if auction_type_data.get('max_price_settings') is False:
                    auction_type_data['max_price_type'] = None
                    auction_type_data['individual_or_max_price'] = None
                    auction_type_data['entire_auction'] = None
                elif auction_type_data.get('max_price_settings') is True:
                    if auction_type_data.get('max_price_type') is None:
                        error = Error(code="AUCTION_02", message=AuctionError.AUCTION_02)
                        raise GraphQLError("err")

                    if auction_type_data.get('individual_or_max_price') is None:
                        error = Error(code="AUCTION_03", message=AuctionError.AUCTION_03)
                        raise GraphQLError("Please check individual or maximum price")

                    if auction_type_data.get('max_price_type') == 1 and auction_type_data.get('individual_or_max_price') == 2:
                        if auction_type_data.entire_auction is None:
                            error = Error(code="AUCTION_04", message=AuctionError.AUCTION_04)
                            raise GraphQLError("Please fill max price for entire Auction.")
                        else:
                            pass
                    else:
                        auction_type_data['entire_auction'] = None

            # --------------------------------------------------------------------------------------------------

            if auction.auction_type1_id == 4:  # Prices
                if auction_type_data.auction_extension is None:
                    error = Error(code="AUCTION_05", message=AuctionError.AUCTION_05)

                    raise GraphQLError("You must type the required auction extension field.")

                # Check of bid mornitoring - views disabled and extension--------------------------------------
                if auction_type_data.type_of_bid_monitoring6 is False:
                    auction_type_data['views_disabled'] = None
                    auction_type_data['minutes'] = None
                elif auction_type_data.type_of_bid_monitoring6 is True:
                    if auction_type_data.views_disabled is None:
                        error = Error(code="AUCTION_06", message=AuctionError.AUCTION_06)
                        raise GraphQLError("You must type the  views disabled required field.")
                    if auction_type_data.views_disabled == 1:
                        auction_type_data['minutes'] = None
                        auction_type_data['type_of_bid_monitoring1'] = False

                    if auction_type_data.views_disabled == 2 and auction_type_data.minutes is None:
                        error = Error(code="AUCTION_07", message=AuctionError.AUCTION_07)
                        raise GraphQLError("Please fill the rest time you want to the information of suppliers be disabled.")

                if auction_type_data.auction_extension == 1:
                    auction_type_data['auction_extension_trigger'] = None
                    auction_type_data['number_of_rankings'] = None
                    auction_type_data['frequency'] = None
                    auction_type_data['trigger_time'] = None
                    auction_type_data['prolongation_by'] = None
                else:

                    if auction_type_data['type_of_bidding'] == 2:
                        auction_type_data['auction_extension_trigger'] = 1
                        auction_type_data['number_of_rankings'] = None
                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None or auction_type_data.trigger_time is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")
                    if auction_type_data['type_of_bidding'] == 1:
                        if auction_type_data.auction_extension_trigger is None:
                            error = Error(code="AUCTION_08", message=AuctionError.AUCTION_08)
                            raise GraphQLError("You must select the way how to trigger when chosing Automatic extension.")

                        if auction_type_data.auction_extension_trigger == 2:
                            if auction_type_data.number_of_rankings is None:
                                error = Error(code="AUCTION_09", message=AuctionError.AUCTION_09)
                                raise GraphQLError("You must type the number of ranking when chosing the second way trigger.")

                            if auction_type_data.number_of_rankings > suppliers_of_auction:
                                error = Error(code="AUCTION_10", message=AuctionError.AUCTION_10)
                                raise GraphQLError("You must type a number lower than or equal to the number of suppliers.")

                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")

                        if auction_type_data.auction_extension_trigger != 2:
                            auction_type_data['number_of_rankings'] = None

                        if auction_type_data.auction_extension_trigger == 3:
                            auction_type_data['trigger_time'] = None
                        else:
                            if auction_type_data.trigger_time is None:
                                error = Error(code="AUCTION_11", message=AuctionError.AUCTION_11)
                                raise GraphQLError("You must type the required trigger time.")
            # --------------------------------------------------------------------------------------------------

            if auction.auction_type1_id == 1:  # Traffic Light
                # ------Check-case-of-bid-mornitoring----------------------------------------
                # ------Check-3rd-then check-or-not-4th----------------------------------------
                # if auction_type_data['type_of_bid_monitoring3'] is False
                # -------Check-6th-then-disabled-all-rest---------------------------------------

                if auction_type_data.type_of_bid_monitoring6 is False:
                    auction_type_data.views_disabled = None
                    auction_type_data['minutes'] = None
                elif auction_type_data.type_of_bid_monitoring6 is True:
                    if auction_type_data.views_disabled is None:
                        error = Error(code="AUCTION_06", message=AuctionError.AUCTION_06)
                        raise GraphQLError("You must type the required views_disabled.")
                    if auction_type_data.views_disabled == 1:
                        auction_type_data['minutes'] = None
                        auction_type_data['type_of_bid_monitoring1'] = False
                        auction_type_data['type_of_bid_monitoring2'] = False
                        auction_type_data['type_of_bid_monitoring3'] = False

                    if auction_type_data.views_disabled == 2 and auction_type_data.minutes is None:
                        error = Error(code="AUCTION_12", message=AuctionError.AUCTION_12)

                        raise GraphQLError("Please fill the time you want to the information of suppliers be disabled.")
            # Ranking
            if auction.auction_type1_id == 3:
                # ------Check-case-of-bid-mornitoring----------------------------------------
                # ------Check-3rd-then check-or-not-4th----------------------------------------

                # -------Check-6th-then-disabled-all-rest---------------------------------------
                if auction_type_data.type_of_bid_monitoring6 is False:
                    auction_type_data['views_disabled'] = None
                    auction_type_data['minutes'] = None
                elif auction_type_data.type_of_bid_monitoring6 is True:
                    if auction_type_data.views_disabled is None:
                        error = Error(code="AUCTION_06", message=AuctionError.AUCTION_06)
                        raise GraphQLError("You must type the required field(s).")
                    if auction_type_data.views_disabled == 1:
                        auction_type_data['minutes'] = None
                        auction_type_data['type_of_bid_monitoring1'] = False
                        auction_type_data['type_of_bid_monitoring3'] = False

                    if auction_type_data.views_disabled == 2 and auction_type_data.minutes is None:
                        error = Error(code="AUCTION_12", message=AuctionError.AUCTION_12)
                        raise GraphQLError("Please fill the time you want to the information of suppliers be disabled.")

                # -------------------------------------------------------------------------------------------------------------
                # ---------Type of bidding affect directly to extension trigger ------------------------------------------------

                if auction_type_data['type_of_bid_monitoring3'] is False:
                    if auction_type_data['type_of_bidding'] == 2:
                        error = Error(code="AUCTION_13", message=AuctionError.AUCTION_13)

                        raise GraphQLError("Default: Bidder sees the best bid ")

                if auction_type_data['auction_extension'] == 1:
                    auction_type_data['auction_extension_trigger'] = None
                    auction_type_data['number_of_rankings'] = None
                    auction_type_data['frequency'] = None
                    auction_type_data['trigger_time'] = None
                    auction_type_data['prolongation_by'] = None
                else:
                    if auction_type_data['type_of_bidding'] == 2:
                        auction_type_data['auction_extension_trigger'] = 1
                        auction_type_data['number_of_rankings'] = None
                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None or auction_type_data.trigger_time is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")
                    if auction_type_data['type_of_bidding'] == 1:
                        if auction_type_data.auction_extension_trigger is None:
                            error = Error(code="AUCTION_08", message=AuctionError.AUCTION_08)
                            raise GraphQLError("You must select the way how to trigger when chosing Automatic extension.")

                        if auction_type_data.auction_extension_trigger == 2:
                            if auction_type_data.number_of_rankings is None:
                                error = Error(code="AUCTION_09", message=AuctionError.AUCTION_09)

                                raise GraphQLError("You must type the number of ranking when chosing the second way trigger.")
                            if auction_type_data.number_of_rankings > suppliers_of_auction:
                                error = Error(code="AUCTION_10", message=AuctionError.AUCTION_10)

                                raise GraphQLError('You must type a number lower than or equal to the number of suppliers.')

                        if auction_type_data.frequency is None or auction_type_data.prolongation_by is None:
                            error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                            raise GraphQLError("You must type the required field(s).")

                        if auction_type_data.auction_extension_trigger != 2:
                            auction_type_data['number_of_rankings'] = None

                        if auction_type_data.auction_extension_trigger == 3:
                            auction_type_data['trigger_time'] = None
                        else:
                            if auction_type_data.trigger_time is None:
                                error = Error(code="AUCTION_11", message=AuctionError.AUCTION_11)

                                raise GraphQLError("You must type the required trigger time.")

                # ----------Check condition of Dutch Auction--------------------
            if auction.auction_type1_id == 5:
                if (
                    auction_type_data.initial_price is None
                    or auction_type_data.end_price is None
                    or auction_type_data.price_step is None
                    or auction_type_data.price_validity is None
                ):
                    error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                    raise GraphQLError("You must type the required field(s).")

                if auction_type_data.initial_price >= auction_type_data.end_price:
                    error = Error(code="AUCTION_16", message=AuctionError.AUCTION_16)

                    raise GraphQLError("Initial price must be lower than end price.")

                if (auction_type_data.initial_price + auction_type_data.price_step) > auction_type_data.end_price:
                    error = Error(code="AUCTION_17", message=AuctionError.AUCTION_17)
                    raise GraphQLError("You must type valid price step.")
                round_auction = (auction_type_data.end_price - auction_type_data.initial_price) / auction_type_data.price_step
                round_auction = math.ceil(round_auction) + 1

            # ----------Check condition of Japanese Auction--------------------
            if auction.auction_type1_id == 6:
                if (
                    auction_type_data.initial_price is None
                    or auction_type_data.end_price is None
                    or auction_type_data.price_step is None
                    or auction_type_data.price_validity is None
                ):
                    error = Error(code="AUCTION_01", message=AuctionError.AUCTION_01)
                    raise GraphQLError("You must type the required field(s).")
                if auction_type_data.initial_price <= auction_type_data.end_price:
                    error = Error(code="AUCTION_18", message=AuctionError.AUCTION_18)

                    raise GraphQLError("Initial price must be greater than end price.")
                if (auction_type_data.initial_price - auction_type_data.price_step) < auction_type_data.end_price:
                    error = Error(code="AUCTION_17", message=AuctionError.AUCTION_17)
                    raise GraphQLError("You must type valid price step.")

                round_auction = (auction_type_data.initial_price - auction_type_data.end_price) / auction_type_data.price_step
                round_auction = math.ceil(round_auction) + 1

            if auction.auction_type1_id == 2:
                auction_type_data['type_of_bid_monitoring6'] = True
                auction_type_data['views_disabled'] = 1
                auction_type_data['auction_extension'] = 1

            # delete or update auction type
            for number_type_id in range(1, 7):
                if number_type_id == 1:
                    if number_type_id != auction.auction_type1_id:
                        AuctionTypeTrafficLight.objects.filter(auction=auction).delete()
                    else:
                        if AuctionTypeTrafficLight.objects.filter(auction=auction).exists():
                            auction_type = AuctionTypeTrafficLight.objects.get(auction=auction)
                        else:
                            auction_type = AuctionTypeTrafficLight()
                        for key, values in auction_type_data.items():
                            if key in [f.name for f in AuctionTypeTrafficLight._meta.get_fields()]:
                                setattr(auction_type, key, values)

                if number_type_id == 2:
                    if number_type_id != auction.auction_type1_id:
                        AuctionTypeSealedBid.objects.filter(auction=auction).delete()
                    else:
                        if AuctionTypeSealedBid.objects.filter(auction=auction).exists():
                            auction_type = AuctionTypeSealedBid.objects.get(auction=auction)
                        else:
                            auction_type = AuctionTypeSealedBid()
                        for key, values in auction_type_data.items():
                            if key in [f.name for f in AuctionTypeSealedBid._meta.get_fields()]:
                                setattr(auction_type, key, values)

                if number_type_id == 3:
                    if number_type_id != auction.auction_type1_id:
                        AuctionTypeRanking.objects.filter(auction=auction).delete()
                    else:
                        if AuctionTypeRanking.objects.filter(auction=auction).exists():
                            auction_type = AuctionTypeRanking.objects.get(auction=auction)
                        else:
                            auction_type = AuctionTypeRanking()
                        for key, values in auction_type_data.items():
                            if key in [f.name for f in AuctionTypeRanking._meta.get_fields()]:
                                setattr(auction_type, key, values)

                if number_type_id == 4:
                    if number_type_id != auction.auction_type1_id:
                        AuctionTypePrices.objects.filter(auction=auction).delete()
                    else:
                        if AuctionTypePrices.objects.filter(auction=auction).exists():
                            auction_type = AuctionTypePrices.objects.get(auction=auction)
                        else:
                            auction_type = AuctionTypePrices()
                        for key, values in auction_type_data.items():
                            if key in [f.name for f in AuctionTypePrices._meta.get_fields()]:
                                setattr(auction_type, key, values)
                if number_type_id == 5:
                    if number_type_id != auction.auction_type1_id:
                        AuctionTypeDutch.objects.filter(auction=auction).delete()
                    else:
                        if AuctionTypeDutch.objects.filter(auction=auction).exists():
                            auction_type = AuctionTypeDutch.objects.get(auction=auction)
                        else:
                            auction_type = AuctionTypePrices()
                        for key, values in auction_type_data.items():
                            if key in [f.name for f in AuctionTypeDutch._meta.get_fields()]:
                                setattr(auction_type, key, values)
                if number_type_id == 6:
                    if number_type_id != auction.auction_type1_id:
                        AuctionTypeJapanese.objects.filter(auction=auction).delete()
                    else:
                        if AuctionTypeDutch.objects.filter(auction=auction).exists():
                            auction_type = AuctionTypeJapanese.objects.get(auction=auction)
                        else:
                            auction_type = AuctionTypePrices()
                        for key, values in auction_type_data.items():
                            if key in [f.name for f in AuctionTypeJapanese._meta.get_fields()]:
                                setattr(auction_type, key, values)
            auction_type.save()

            # ---Case: entire Auction--------Calculate the average of all items and compare to max price of all items----------------
            # ---Case: True, 1, 2---------------------database  updated-------------------------

            if (
                auction.auction_type1_id == 1 or auction.auction_type1_id == 3 or auction.auction_type1_id == 4
            ):  # add this line as Sealed bid dooes not have fields about max price
                if auction_type.max_price_settings is True and auction_type.max_price_type == 1 and auction_type.individual_or_max_price == 2:
                    average_price_total = 0
                    price_item = 0
                    for item in input.auction_items:
                        for supplier in item['suppliers']:
                            price_item = price_item + supplier['price']
                        average_price_total = price_item / len(item['suppliers'])

                    for item in input.auction_items:
                        item['max_price'] = None

                    max_price_all_items = auction_type_data['entire_auction']

                    percent = 0.8
                    bounded_max_price = percent * average_price_total
                    error_max_and_average_total = abs(max_price_all_items - average_price_total)

                    if error_max_and_average_total > bounded_max_price:
                        error = Error(code="AUCTION_19", message=AuctionError.AUCTION_19)
                        raise GraphQLError(
                            "You choose max price for entire Auction. \n Please fill in max price such that value of all items between 0,2 and 1,8 average of all items."
                        )
            # ----------------------------------------------------------------------------
            user_buyer = User.objects.select_related('buyer').get(id=auction.user_id)
            # Start to save items
            list_item_id_input = []

            for item in input.auction_items:
                auction_item_data = item
                auction_item_data['auction'] = auction
                if auction.auction_type1_id == 1:  # Traffic Light
                    if (
                        auction_item_data.target_price is None
                        or auction_item_data.price_yellow is None
                        or auction_item_data.minimum_bid_step is None
                        or auction_item_data.maximum_bid_step is None
                    ):
                        error = Error(code="AUCTION_20", message=AuctionError.AUCTION_20)
                        raise GraphQLError(
                            " Please check price level for yellow, target price, minimum bid step and maximum bid step, maybe one of these fields be incomplete"
                        )

                    if (
                        auction_type.max_price_settings is True
                        and auction_type.max_price_type == 2
                        and auction_type.individual_or_max_price == 2
                        and auction_item_data.max_price is None
                    ):
                        error = Error(code="AUCTION_21", message=AuctionError.AUCTION_21)

                        raise GraphQLError("Please fill value of max price for all items as chosing setting True")

                    if auction_type.max_price_settings is False:
                        auction_item_data['max_price'] = None

                    if auction_type.individual_or_max_price == 1:
                        auction_item_data['max_price'] = None

                if auction.auction_type1_id == 3 or auction.auction_type1_id == 4:  # Ranking-Prices
                    auction_item_data['price_yellow'] = None

                    if auction_item_data.minimum_bid_step is None or auction_item_data.maximum_bid_step is None:
                        error = Error(code="AUCTION_14", message=AuctionError.AUCTION_14)
                        raise GraphQLError("Please fill in minimum bid step and maximum bid step.")
                    if (
                        auction_type.max_price_settings is True
                        and auction_type.max_price_type == 2
                        and auction_type.individual_or_max_price == 2
                        and auction_item_data.max_price is None
                    ):
                        error = Error(code="AUCTION_21", message=AuctionError.AUCTION_21)
                        raise GraphQLError("Please fill value of max price for all items as chosing setting True")

                    if auction_type.max_price_settings is False:
                        auction_item_data['max_price'] = None

                    if auction_type.individual_or_max_price == 1:
                        auction_item_data['max_price'] = None

                if auction.auction_type1_id == 2 or auction.auction_type1_id == 5 or auction.auction_type1_id == 6:  # Sealed Bid #Dutch #Japanese
                    auction_item_data['price_yellow'] = None
                    auction_item_data['target_price'] = None
                    auction_item_data['minimum_bid_step'] = None
                    auction_item_data['maximum_bid_step'] = None
                    auction_item_data['max_price'] = None

                # ---Case: Per position--------Calculate the average of each item and compare to max price of each item----------------
                # ---Case: True, 2, 2 ------------------------------------------------------------------------
                if (
                    auction.auction_type1_id == 1 or auction.auction_type1_id == 3 or auction.auction_type1_id == 4
                ):  # add this line as Sealed bid dooes not have fields about max price
                    if auction_type.max_price_settings is True and auction_type.max_price_type == 2 and auction_type.individual_or_max_price == 2:
                        price_item = 0
                        for supplier in item['suppliers']:
                            price_item = price_item + supplier['price']

                        average_price_item = price_item / len(item['suppliers'])
                        bounded_max_price = 0.8 * average_price_item
                        error_max_and_start = abs(auction_item_data['max_price'] - average_price_item)

                        if error_max_and_start > bounded_max_price:
                            error = Error(code="AUCTION_15", message=AuctionError.AUCTION_15)
                            raise GraphQLError(
                                "You set max price per position. \n Please fill value of max price not greater or lower than 80 percent average value of suppliers for each item."
                            )
                auction_suppliers_mapping = AuctionSupplier.objects.filter(auction=auction)
                auction_items_mapping = AuctionItem.objects.filter(auction_id=auction.id)

                item_data = {}
                for key, values in auction_item_data.items():
                    if key in [f.name for f in AuctionItem._meta.get_fields()]:
                        if key == "unit":
                            values = UnitofMeasure.objects.get(id=values)
                        if key == "id":
                            values = int(values)
                        if key != "suppliers":
                            item_data[key] = values
                auction_item = AuctionItem.objects.update_or_create(id=item_data.get('id'), defaults=item_data)[0]
                list_item_id_input.append(auction_item.id)
                # --------------------------------------------------------------------------
                list_supplier_id_input = []
                for supplier in item.suppliers:
                    auction_supplier_data = supplier
                    auction_supplier_data['auction'] = auction
                    auction_supplier_data['supplier_status'] = 1
                    if AuctionSupplier.objects.filter(auction=auction, user_id=supplier['user']).exists():
                        auction_supplier = AuctionSupplier.objects.get(auction_id=auction.id, user_id=supplier['user'])
                    else:
                        auction_supplier = AuctionSupplier()
                    for key, values in auction_supplier_data.items():
                        if key in [f.name for f in AuctionSupplier._meta.get_fields()]:
                            if key == "user":
                                values = User.objects.get(id=values)
                            setattr(auction_supplier, key, values)
                    auction_supplier.save()
                    list_supplier_id_input.append(auction_supplier.id)

                    auction_item_supplier_data = supplier
                    auction_item_supplier_data["auction"] = auction
                    auction_item_supplier_data["auction_item"] = auction_item
                    auction_item_supplier_data["auction_supplier"] = auction_supplier
                    data = {}
                    for key, values in auction_item_supplier_data.items():
                        if key in [f.name for f in AuctionItemSupplier._meta.get_fields()]:
                            if key == "user":
                                values = User.objects.get(id=values)
                            data[key] = values

                    auction_item_supplier = AuctionItemSupplier.objects.update_or_create(
                        auction_item=data.get('auction_item'), auction_supplier=data.get('auction_supplier'), defaults=data
                    )[0]

            # ---------------------------delete-----------------
            auction_suppliers = {data.id: data for data in auction_suppliers_mapping}
            auction_item_list = {data.id: data for data in auction_items_mapping}
            for item_id in auction_item_list:
                if item_id not in list_item_id_input:
                    AuctionItem.objects.filter(id=item_id).delete()

            for id in auction_suppliers:
                if id not in list_supplier_id_input:
                    auction_supplier = AuctionSupplier.objects.get(auction=auction, id=id)
                    AuctionItemSupplier.objects.filter(id=id).delete()
                    auction_supplier.delete()
            if auction.status == 2:
                # send mail
                send_mail_published_auction(auction=auction)
            return AuctionUpdate(auction=auction, status=True)

        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return AuctionUpdate(status=False, error=error)

def send_mail_published_auction(auction):
    supplier_price_list = []
    # send supplier
    user_buyer = auction.user
    auction_suppliers = AuctionSupplier.objects.filter(auction=auction)
    for supplier in auction_suppliers:
        user_supplier = supplier.user
        if auction.coupon:
            price = AuctionItemSupplier.objects.filter(auction=auction, auction_supplier=supplier).aggregate(Sum('price'))
            supplier_price_list.append(price.get('price__sum'))

        tz = pytz.timezone(user_supplier.local_time)
        start_time = auction.start_time.replace(tzinfo=pytz.utc).astimezone(tz)
        email_supplier_auction = EmailTemplatesTranslation.objects.filter(
            email_templates__item_code="SupplierCreateAuction", language_code=user_supplier.language.item_code
        )
        if not email_supplier_auction:
            email_supplier_auction = EmailTemplates.objects.filter(item_code="SupplierCreateAuction")
        email_supplier_auction = email_supplier_auction.first()
        email_supplier = Template(email_supplier_auction.content).render(
            Context(
                {
                    "image": "https://api.nextpro.io/static/logo_mail.png",
                    "name": user_supplier.full_name,
                    "company_long_name": user_buyer.buyer.company_full_name,
                    "auction_title": auction.title,
                    "auction_item_code": auction.item_code,
                    "start_time_date": start_time.strftime('%Y/%m/%d'),
                    "start_time": start_time.strftime('%H:%M'),
                    "AuctionID": auction.id,
                }
            )
        )
        try:
            send_mail(
                email_supplier_auction.title,
                email_supplier,
                "NextPro <no-reply@nextpro.io>",
                [user_supplier.email],
                html_message=email_supplier,
                fail_silently=True,
            )
        except:
            print("Fail mail2")
    # send buyer
    email_buyer_auction = EmailTemplatesTranslation.objects.filter(
        email_templates__item_code="BuyerCreateAuction", language_code=user_buyer.language.item_code
    )
    if not email_buyer_auction:
        email_buyer_auction = EmailTemplates.objects.filter(item_code="BuyerCreateAuction")
    email_buyer_auction = email_buyer_auction.first()
    email_buyer = Template(email_buyer_auction.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": user_buyer.full_name,
                "auction_title": auction.title,
                "auction_item_code": auction.item_code,
            }
        )
    )
    title = Template(email_buyer_auction.title).render(Context({"auction_item_code": auction.item_code,}))
    try:
        send_mail(
            title, email_buyer, "NextPro <no-reply@nextpro.io>", [user_buyer.email], html_message=email_buyer, fail_silently=True,
        )
    except:
        print("Fail mail1")

    # send email coupon
    if auction.coupon:
        coupon = Coupon.objects.filter(coupon_program=auction.coupon, status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
        if coupon.exists():
            coupon = coupon.first()
            email_coupon = EmailTemplates.objects.get(item_code="CouponPublishedAuction")
            title = Template(email_coupon.title).render(Context({'code': coupon.coupon_program}))
            email = Template(email_coupon.content).render(
                Context(
                    {
                        "image": "https://api.nextpro.io/static/logo_mail.png",
                        "name": coupon.full_name,
                        "buyer_name": user_buyer.full_name,
                        "auction_title": auction.title,
                        "auction_no": auction.item_code,
                        "min_supplier_quote": str("{:10,.2f}".format(round(min(supplier_price_list)))) + " VND",
                        "max_supplier_quote": str("{:10,.2f}".format(round(max(supplier_price_list)))) + " VND",
                    }
                )
            )
            try:
                send_mail(
                    title, email, "NextPro <no-reply@nextpro.io>", [coupon.email], html_message=email, fail_silently=True,
                )
            except:
                print("Fail mail9")


def check_number_auction_buyer(user):
    list_id = []
    if user.company_position == 1:
        buyer = Buyer.objects.get(user=user)
        buyer_auction = buyer.profile_features.no_eauction_year
        list_sub_accounts = BuyerSubAccounts.objects.filter(buyer=buyer)
        for ob in list_sub_accounts:
            list_id.append(ob.user_id)
        list_id.append(buyer.user_id)

    else:
        buyer_sub_account = BuyerSubAccounts.objects.get(user=user)
        buyer = Buyer.objects.get(id=buyer_sub_account.buyer_id)
        buyer_auction = buyer.profile_features.no_eauction_year
        list_sub_accounts = BuyerSubAccounts.objects.filter(buyer_id=buyer.id)
        for ob in list_sub_accounts:
            list_id.append(ob.user_id)
        list_id.append(buyer.user_id)

    count = Auction.objects.filter(user_id__in=list_id).count()
    # send limit auction
    if (count + 1) == buyer_auction:
        email_auction_limit = EmailTemplatesTranslation.objects.filter(
            email_templates__item_code="LimitAuction", language_code=user.language.item_code
        )
        if not email_auction_limit:
            email_auction_limit = EmailTemplates.objects.filter(item_code="LimitAuction")
        email_auction_limit = email_auction_limit.first()
        email = Template(email_auction_limit.content).render(
            Context({"image": "https://api.nextpro.io/static/logo_mail.png", "name": user.full_name, "link": "http://192.168.9.94:9001/account",})
        )
        try:
            send_mail(
                email_auction_limit.title, email, "NextPro <no-reply@nextpro.io>", [user.email], html_message=email, fail_silently=True,
            )
        except:
            print("Fail mail11")

    if count < buyer_auction:
        return True
    return False

class AuctionTypeSuggestion(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    auction_type_id = graphene.Int()

    class Arguments:
        input = graphene.List(graphene.Float, required=True)

    def mutate(root, info, input):
        if len(input) > 5:
            error = Error(code="AUCTION_27", message=AuctionError.AUCTION_27)
            return AuctionTypeSuggestion(status=False, error=error)
        if len(input) == 0:
            return AuctionTypeSuggestion(status=True, auction_type_id=None)
        min_value = min(input)
        average = sum(input) / len(input)
        percentage = abs((min_value / average - 1) * 100)

        if len(input) == 1 or (len(input) == 2 and percentage > 10) or (len(input) >= 3 and percentage > 10):
            return AuctionTypeSuggestion(status=True, auction_type_id=1)
        elif (len(input) == 2 and 0 <= percentage <= 10) or (len(input) >= 3 and 5 < percentage <= 10):
            return AuctionTypeSuggestion(status=True, auction_type_id=3)
        elif len(input) >= 3 and 0 <= percentage <= 5:
            return AuctionTypeSuggestion(status=True, auction_type_id=4)
        else:
            return AuctionTypeSuggestion(status=True, auction_type_id=None)

class ItemConfirm(graphene.InputObjectType):
    auction_item_id = graphene.String(required=True)
    confirm_price = graphene.Float(required=True)

class AuctionConfirmInput(graphene.InputObjectType):
    auction_id = graphene.String(required=True)
    supplier_status = graphene.Int(required=True)
    is_accept = graphene.Boolean(required=True)
    note_from_supplier = graphene.String()
    items = graphene.List(ItemConfirm, required=True)
    is_accept_rule = graphene.Boolean(required=True)


class AuctionConfirm(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    history = graphene.Field(HistoryNode)

    class Arguments:
        input = AuctionConfirmInput(required=True)

    def mutate(root, info, input):
        try:
            error = None
            try:
                user = GetToken.getToken(info).user
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
            auction = Auction.objects.get(pk=input.auction_id)
            options = auction.get_options()

            auction_supplier = AuctionSupplier.objects.get(auction=auction, user=user)
            auction_item = AuctionItem.objects.filter(auction=auction)
            auction_items_supplier = AuctionItemSupplier.objects.filter(auction=auction, auction_supplier=auction_supplier)

            if auction_supplier.supplier_status != 1:
                return AuctionConfirm(status=False)

            if input.supplier_status not in (1, 3) or auction_supplier.is_accept == True:
                return AuctionConfirm(status=False)

            auction_supplier.supplier_status = input.supplier_status
            auction_supplier.is_accept = input.is_accept
            auction_supplier.note_from_supplier = input.note_from_supplier
            auction_supplier.is_accept_rule = input.is_accept_rule
            if input.supplier_status == 1:
                percent = 0.8
                # Check confirm price of each item that supplier type--------------------------
                if auction.auction_type1_id == 1 or auction.auction_type1_id == 3 or auction.auction_type1_id == 4:
                    # Case 1: (False, Null, Null)
                    if options.max_price_settings is False:
                        for data in input.items:
                            data['auction_item_id'] = int(data['auction_item_id'])
                            for item in auction_item:

                                auction_item_supplier = AuctionItemSupplier.objects.get(
                                    auction=auction, auction_item_id=item.id, auction_supplier_id=auction_supplier.id
                                )

                                if auction_item_supplier.auction_item_id == data['auction_item_id']:

                                    if data['confirm_price'] is None:
                                        error = Error(code="AUCTION_28", message=AuctionError.AUCTION_28)
                                        raise GraphQLError('Please fill value of changed starting price.')

                                    error_confirm_and_start = abs(data['confirm_price'] - auction_item_supplier.price)
                                    bounded_starting_price = auction_item_supplier.price * percent
                                    if error_confirm_and_start > bounded_starting_price:
                                        error = Error(code="AUCTION_29", message=AuctionError.AUCTION_29)
                                        raise GraphQLError('Your new starting price not be greater or lower 80 percent than starting price')
                    # Case 2: (True, 1, 1)
                    if options.max_price_settings is True and options.max_price_type == 1 and options.individual_or_max_price == 1:

                        for data in input.items:
                            data['auction_item_id'] = int(data['auction_item_id'])

                            for item in auction_item:

                                auction_item_supplier = AuctionItemSupplier.objects.get(
                                    auction=auction, auction_item_id=item.id, auction_supplier_id=auction_supplier.id
                                )

                                if auction_item_supplier.auction_item_id == data['auction_item_id']:

                                    if data['confirm_price'] is None:
                                        error = Error(code="AUCTION_28", message=AuctionError.AUCTION_28)
                                        raise GraphQLError('Please fill value of changed starting price.')

                        total_confirm_price = 0
                        for data in input.items:
                            total_confirm_price = total_confirm_price + data['confirm_price']

                        total_starting_price = 0
                        for item_supplier in auction_items_supplier:
                            total_starting_price = total_starting_price + item_supplier.price

                        error_confirm_and_start = abs(total_confirm_price - total_starting_price)
                        bounded_confirm_price = total_starting_price * percent

                        if (total_confirm_price > total_starting_price) or (error_confirm_and_start > bounded_confirm_price):
                            error = Error(code="AUCTION_30", message=AuctionError.AUCTION_30)
                            raise GraphQLError(
                                'Total of confirm price not be greater than total of your starting price and error not over 80 percent of starting price.'
                            )

                    # Case 3: (True, 2, 1)
                    if options.max_price_settings is True and options.max_price_type == 2 and options.individual_or_max_price == 1:

                        for data in input.items:
                            data['auction_item_id'] = int(data['auction_item_id'])

                            for item in auction_item:

                                auction_item_supplier = AuctionItemSupplier.objects.get(
                                    auction=auction, auction_item_id=item.id, auction_supplier_id=auction_supplier.id
                                )

                                if auction_item_supplier.auction_item_id == data['auction_item_id']:

                                    if data['confirm_price'] is None:
                                        error = Error(code="AUCTION_28", message=AuctionError.AUCTION_28)
                                        raise GraphQLError('Please fill value of changed starting price.')

                                    error_confirm_and_start = abs(data['confirm_price'] - auction_item_supplier.price)
                                    bounded_starting_price = auction_item_supplier.price * percent

                                    if (data['confirm_price'] > auction_item_supplier.price) or (error_confirm_and_start > bounded_starting_price):
                                        error = Error(code="AUCTION_29", message=AuctionError.AUCTION_29)
                                        raise GraphQLError(
                                            'Your new starting price not be greater than starting price and error not over 80 percent of starting price.'
                                        )

                    # Case 4: (True, 2, 2)
                    if options.max_price_settings is True and options.max_price_type == 2 and options.individual_or_max_price == 2:
                        for data in input.items:
                            data['auction_item_id'] = int(data['auction_item_id'])

                            for item in auction_item:

                                auction_item_supplier = AuctionItemSupplier.objects.get(
                                    auction=auction, auction_item_id=item.id, auction_supplier_id=auction_supplier.id
                                )
                                max_price_item = item.max_price

                                if auction_item_supplier.auction_item_id == data['auction_item_id']:

                                    if data['confirm_price'] is None:
                                        error = Error(code="AUCTION_28", message=AuctionError.AUCTION_28)

                                        raise GraphQLError('Please fill value of changed starting price.')

                                    error_confirm_and_max = abs(data['confirm_price'] - max_price_item)
                                    bounded_max_price = max_price_item * percent

                                    if (data['confirm_price'] > max_price_item) or (error_confirm_and_max > bounded_max_price):
                                        error = Error(code="AUCTION_29", message=AuctionError.AUCTION_29)
                                        raise GraphQLError(
                                            'Your new starting price not be greater than max price and error not over 80 percent of maxw price.'
                                        )

                    # Case 5: (True, 1, 2)
                    if options.max_price_settings is True and options.max_price_type == 1 and options.individual_or_max_price == 2:
                        for data in input.items:
                            data['auction_item_id'] = int(data['auction_item_id'])

                            for item in auction_item:

                                auction_item_supplier = AuctionItemSupplier.objects.get(
                                    auction=auction, auction_item_id=item.id, auction_supplier_id=auction_supplier.id
                                )

                                if auction_item_supplier.auction_item_id == data['auction_item_id']:

                                    if data['confirm_price'] is None:
                                        error = Error(code="AUCTION_28", message=AuctionError.AUCTION_28)
                                        raise GraphQLError('Please fill value of changed starting price.')

                        total_confirm_price = 0
                        for data in input.items:
                            total_confirm_price = total_confirm_price + data['confirm_price']

                        total_max_price = options.entire_auction

                        error_confirm_and_max = abs(total_confirm_price - total_max_price)
                        bounded_max_price = total_max_price * percent

                        if (total_confirm_price > total_max_price) or (error_confirm_and_max > bounded_max_price):
                            error = Error(code="AUCTION_30", message=AuctionError.AUCTION_30)
                            raise GraphQLError(
                                'Total of confirm price not be greater than max price and error not over 80 percent of starting price.'
                            )

                if auction.auction_type1_id == 2:
                    for data in input.items:
                        data['auction_item_id'] = int(data['auction_item_id'])

                        for item in auction_item:

                            auction_item_supplier = AuctionItemSupplier.objects.get(
                                auction=auction, auction_item_id=item.id, auction_supplier_id=auction_supplier.id
                            )

                            if auction_item_supplier.auction_item_id == data['auction_item_id']:

                                if data['confirm_price'] is None:
                                    error = Error(code="AUCTION_28", message=AuctionError.AUCTION_28)

                                    raise GraphQLError('Please fill value of changed starting price.')

                                error_confirm_and_start = abs(data['confirm_price'] - auction_item_supplier.price)
                                bounded_starting_price = auction_item_supplier.price * percent

                                if (error_confirm_and_start > bounded_starting_price) or (data['confirm_price'] > auction_item_supplier.price):
                                    error = Error(code="AUCTION_29", message=AuctionError.AUCTION_29)
                                    raise GraphQLError('Your new starting price not be greater 80 percent than starting price.')

            auction_supplier.save()
            amount = 0
            for data in input.items:
                if auction.auction_type1_id == 5 or auction.auction_type1_id == 6:
                    data['auction_item_id'] = int(data['auction_item_id'])
                for item in auction_item:
                    auction_item_supplier = AuctionItemSupplier.objects.get(
                        auction_id=auction, auction_item_id=item.id, auction_supplier_id=auction_supplier.id
                    )
                    if data['auction_item_id'] == item.id:

                        if input.supplier_status == 1:
                            auction_item_supplier.auction_item_id = data['auction_item_id']
                            auction_item_supplier.confirm_price = data['confirm_price']
                            amount += float(data['confirm_price'])
                        if input.supplier_status == 3:
                            auction_item_supplier.auction_item_id = data['auction_item_id']
                            auction_item_supplier.confirm_price = None
                        auction_item_supplier.save()
            if auction_supplier.supplier_status == 3:
                return AuctionConfirm(status=True)
            # payment
            if auction.auction_next_round is not None:
                payment_auction = PaymentAuction.objects.filter(auction_id=auction.auction_next_round, history__user_payment__user=user).first()
                payment_auction.auction = auction
                payment_auction.save()
                auction_supplier.supplier_status = 5
                auction_supplier.save()
                history = payment_auction.history
            else:
                platform_fee = PlatformFee.objects.all().first()
                amount_usd = amount
                auction_fee = AuctionFee.objects.filter(min_value__lte=amount_usd, max_value__gte=amount_usd)
                auction_fee = auction_fee.first()
                if auction_fee is None:
                    value = AuctionFee.objects.filter().aggregate(Max('max_value'))
                    auction_fee = AuctionFee.objects.filter(max_value=value.get('max_value__max')).first()
                amount = (amount * auction_fee.percentage) / 100
                amount_payment = amount + platform_fee.fee
                detail = [
                    {'description': f'''Deposit {auction.item_code}''', 'quantity': 1, 'unit_price': amount_payment, 'total_amount': amount_payment,}
                ]
                sub_total = round(amount_payment)
                charge_amount = round(platform_fee.fee * 1.1)
                amount_payment = round(amount_payment + amount_payment * 0.1)
                order_no = History.objects.filter().count() + 1
                order_no = '70' + str(order_no).zfill(4)
                history = History.objects.create(
                    user_payment=user.user_payment,
                    type=2,
                    transaction_description=f'''Deposit {auction.item_code}''',
                    balance=0,
                    status=1,
                    order_no=order_no,
                    amount=amount_payment,
                )
                payment_auction = PaymentAuction.objects.create(auction=auction, charge_amount=charge_amount, refund_amount=0, history=history)

                data = {
                    'user': user,
                    'invoice_no': history.order_no,
                    'invoice_date': datetime.strftime(history.date, '%d-%m-%Y'),
                    'detail_list': detail,
                    'sub_total': sub_total,
                    'is_topup': False,
                }

                invoice_generate(data)
                request_draft_invoice = f'''/{user.id}/{history.order_no}/draft_invoice.pdf'''
                history.request_draft_invoice = request_draft_invoice
                history.save()

            return AuctionConfirm(status=True, history=history)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return AuctionConfirm(status=False, error=error)

class AuctionCanncel(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    auction = graphene.Field(AuctionNode)
    class Arguments:
        id = graphene.String(required=True)
        reason = graphene.String()
    def mutate(root, info, id,reason=None):
        try:
            auction = Auction.objects.get(id = id)
            if auction.status == 4:
                auction.status =6
                auction.save()
                AuctionSupplier.objects.filter(supplier_status=6, auction=auction).update(awarded=3, supplier_status=8)
                supplier_canncels = AuctionSupplier.objects.filter(auction=auction, supplier_status=8)
                for supplier_canncel in supplier_canncels:
                    send_mail_canncel_auction_supplier(item_code="CanncelAuctionSupplier", supplier =supplier_canncel,reason=reason,auction=auction)
                send_mail_canncel_auction_buyer(auction=auction,buyer=auction.user.buyer,reason= reason,item_code="CanncelAuctionBuyer")
                return AuctionCanncel(status=  True,auction=auction)
            else:
                raise GraphQLError("errors")
        except Auction.DoesNotExist:
            error = Error(code="AUCTION_31", message=AuctionError.AUCTION_31)
            return AuctionCanncel(status = False, error = error)

class AuctionNextRoundRefund(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    auction = graphene.Field(AuctionNode)
    class Arguments:
        auction_id = graphene.String(required=True)
        list_user_id = graphene.List(graphene.String,required =True)
    def mutate(root, info, auction_id,list_user_id):
        try:
            list_user_id = map(lambda x: x, list_user_id)
            auction = Auction.objects.get(id = auction_id)
            AuctionSupplier.objects.filter(supplier_status=6, auction=auction,user_id__in = list_user_id).update(awarded=3, supplier_status=8)
            supplier_canncels = AuctionSupplier.objects.filter(auction=auction, supplier_status=8)
            supplier_next_rounds = AuctionSupplier.objects.filter(auction=auction, supplier_status=8,awarded=3)
            for supplier_next_round in supplier_next_rounds:
                send_mail_award("RefundedDepositMyAccount", supplier_next_round)
            return AuctionNextRoundRefund(status= True,auction=auction)
        except Auction.DoesNotExist:
            error = Error(code="AUCTION_31", message=AuctionError.AUCTION_31)
            return AuctionNextRoundRefund(status = False, error = error)

class ReSendInviteSupplier(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        auction_id = graphene.String(required=True)
        email = graphene.String(required =True)

    def mutate(root, info, auction_id, email):
        try:
            auction = Auction.objects.get(id = auction_id)
            if not AuctionSupplier.objects.filter(supplier_status=1, auction=auction, user__email=email, user__user_type=3).exists():
                error = Error(code="AUCTION_32", message=AuctionError.AUCTION_32)
                return ReSendInviteSupplier(error=error)
            auction_supplier = AuctionSupplier.objects.filter(auction=auction, user__email=email, user__user_type=3).first()
            user_supplier = auction_supplier.user
            user_buyer = auction.user
            supplier_price_list = []
            if auction.coupon:
                price = AuctionItemSupplier.objects.filter(auction=auction, auction_supplier=auction_supplier).aggregate(Sum('price'))
                supplier_price_list.append(price.get('price__sum'))

            tz = pytz.timezone(user_supplier.local_time)
            start_time = auction.start_time.replace(tzinfo=pytz.utc).astimezone(tz)
            email_supplier_auction = EmailTemplatesTranslation.objects.filter(
                email_templates__item_code="SupplierCreateAuction", language_code=user_supplier.language.item_code
            )
            if not email_supplier_auction:
                email_supplier_auction = EmailTemplates.objects.filter(item_code="SupplierCreateAuction")
            email_supplier_auction = email_supplier_auction.first()
            email_supplier = Template(email_supplier_auction.content).render(
                Context(
                    {
                        "image": "https://api.nextpro.io/static/logo_mail.png",
                        "name": user_supplier.full_name,
                        "company_long_name": user_buyer.buyer.company_full_name,
                        "auction_title": auction.title,
                        "auction_item_code": auction.item_code,
                        "start_time_date": start_time.strftime('%Y/%m/%d'),
                        "start_time": start_time.strftime('%H:%M'),
                        "AuctionID": auction.id,
                    }
                )
            )
        
            try:
                send_mail(
                    email_supplier_auction.title,
                    email_supplier,
                    "NextPro <no-reply@nextpro.io>",
                    [user_supplier.email],
                    html_message=email_supplier,
                    fail_silently=True,
                )
            except:
                print("Fail mail")
            # send buyer
            email_buyer_auction = EmailTemplatesTranslation.objects.filter(
                email_templates__item_code="BuyerCreateAuction", language_code=user_buyer.language.item_code
            )
            if not email_buyer_auction:
                email_buyer_auction = EmailTemplates.objects.filter(item_code="BuyerCreateAuction")
            email_buyer_auction = email_buyer_auction.first()
            email_buyer = Template(email_buyer_auction.content).render(
                Context(
                    {
                        "image": "https://api.nextpro.io/static/logo_mail.png",
                        "name": user_buyer.full_name,
                        "auction_title": auction.title,
                        "auction_item_code": auction.item_code,
                    }
                )
            )
            title = Template(email_buyer_auction.title).render(Context({"auction_item_code": auction.item_code,}))
            try:
                send_mail(
                    title, email_buyer, "NextPro <no-reply@nextpro.io>", [user_buyer.email], html_message=email_buyer, fail_silently=True,
                )
            except:
                print("Fail mail")
            # send email coupon
            if auction.coupon:
                coupon = Coupon.objects.filter(coupon_program=auction.coupon, status=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
                if coupon.exists():
                    coupon = coupon.first()
                    email_coupon = EmailTemplates.objects.get(item_code="CouponPublishedAuction")
                    title = Template(email_coupon.title).render(Context({'code': coupon.coupon_program}))
                    email = Template(email_coupon.content).render(
                        Context(
                            {
                                "image": "https://api.nextpro.io/static/logo_mail.png",
                                "name": coupon.full_name,
                                "buyer_name": user_buyer.full_name,
                                "auction_title": auction.title,
                                "auction_no": auction.item_code,
                                "min_supplier_quote": str("{:10,.2f}".format(round(min(supplier_price_list)))) + " VND",
                                "max_supplier_quote": str("{:10,.2f}".format(round(max(supplier_price_list)))) + " VND",
                            }
                        )
                    )
                    try:
                        root.mail = send_mail(title, email, "NextPro <no-reply@nextpro.io>", [coupon.email],
                                              html_message=email, fail_silently=True, )
                    except:
                        print("Fail mail")
            return ReSendInviteSupplier(status= True)
        except Auction.DoesNotExist:
            error = Error(code="AUCTION_31", message=AuctionError.AUCTION_31)
            return ReSendInviteSupplier(status = False, error = error)

class Mutation(graphene.ObjectType):
    auction_award_create = AuctionAwardCreate.Field()

    auction_create = AuctionCreate.Field()
    auction_update = AuctionUpdate.Field()

    auction_type_suggestion = AuctionTypeSuggestion.Field()

    auction_confirm = AuctionConfirm.Field()

    auction_canncel  = AuctionCanncel.Field()
    
    auction_next_round_refund = AuctionNextRoundRefund.Field()
    
    re_send_invite_supplier= ReSendInviteSupplier.Field()
