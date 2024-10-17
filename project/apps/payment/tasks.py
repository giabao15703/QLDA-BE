from celery import Celery
import binascii
import hmac
import hashlib
import requests
from apps.payment.models import History, HistoryOnePay, PaymentAuction, HistoryPending
from apps.payment.schema import send_mail_sicp, send_mail_upgraded
from django.utils import timezone
from apps.auctions.models import AuctionSupplier
from datetime import datetime
from django.conf import settings


app = Celery('apps', broker=settings.RABBITMQ_URL)


@app.task(name='apps.payment.tasks.check_one_pay')
def check_one_pay():
    histories = History.objects.filter(status=7, method_payment=3).exclude(type=4)
    for history in histories:
        history_one_pay = HistoryOnePay.objects.filter(history=history).first()
        user_payment = history.user_payment
        date = datetime.strftime(history.date, '%Y%m%d%H%M%S')
        vpc_MerchTxnRef = history.order_no + "-" + date
        values = {
            'vpc_AccessCode': '6BEB2546',
            'vpc_Command': 'queryDR',
            'vpc_MerchTxnRef': vpc_MerchTxnRef,
            'vpc_Merchant': 'TESTONEPAY',
            'vpc_Password': 'op123456',
            'vpc_User': 'op01',
            'vpc_Version': '1',
        }
        result = query_DR_api(values)
        if result is None:
            pass
        elif result.get('vpc_DRExists') == "N":
            history.status = 6
        elif result.get('vpc_TxnResponseCode') == '0':
            if history.type == 3:
                user_payment.one_pay = user_payment.one_pay + history.balance
                history.status = 2
            elif history.type == 1:
                user = user_payment.user
                history.status = 2
                products = []
                discount_promotion = None
                discountContent = None
                amount_sicp_registration = 0
                amount_profile_features = 0
                promotion = history_one_pay.promotion
                if user.isBuyer():
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
                            "taxRateId": None,
                            "extraFields": [],
                            "subTotal": amount_profile_features,
                            "hidePrice": False,
                        }
                    )

                if user.isSupplier():
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
                    user.supplier.save()
                if promotion is not None:
                    discount_promotion = promotion.discount
                    discountContent = promotion.description

                # e-invoice
                data = {
                    "history": history,
                    "user": user,
                    "type": history.method_payment,
                    "product": products,
                    "discount": discount_promotion,
                    "discountContent": discountContent,
                }
            elif history.type == 2:
                history_parent = history
                if history.is_parent == False:
                    history_pending = HistoryPending.objects.filter(history_pending=history).first()
                    history_parent = history_pending.history
                payment_auction = PaymentAuction.objects.filter(history=history_parent).order_by('-id').first()
                auction_supplier = AuctionSupplier.objects.filter(auction=payment_auction.auction, user=user_payment.user).first()
                auction_supplier.supplier_status = 5
                history.status = 2
                auction_supplier.save()

            else:
                print("error")

        elif result.get('vpc_TxnResponseCode') == '300' or result.get('vpc_TxnResponseCode') == '100':
            pass
        else:
            history.status = 6

        history.save()


def query_DR_api(values):
    key = "6D0870CDE5F24F34F3915FB0045120DB"
    message = str(values)
    message = message.replace("': '", "=").replace("', '", "&").replace("{'", "").replace("'}", "").encode()
    vpc_SecureHash = hmac.new(binascii.unhexlify(key), message, hashlib.sha256).hexdigest().upper()
    values['vpc_SecureHash'] = vpc_SecureHash
    url = "https://mtf.onepay.vn/msp/api/v1/vpc/invoices/queries"
    r = requests.post(url, data=values)
    response = r.content.decode("utf-8").split("&")
    print(response)
    data = {}
    try:
        for y in response:
            y = y.split('=')
            if len(y) > 0:
                data[y[0]] = y[1]
        return {'vpc_TxnResponseCode': data.get('vpc_TxnResponseCode'), 'vpc_DRExists': data.get('vpc_DRExists')}
    except:
        return None
