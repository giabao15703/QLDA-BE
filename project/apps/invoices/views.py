import codecs
import json
import inflect
import pdfkit
import requests

from apps.users.models import Buyer, Supplier
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from pathlib import Path

# -------------------------------Draft Invoice-----------------------------------------
def invoice_generate(data):
    data = data
    user = data['user']
    if user.isBuyer():
        buyer = Buyer.objects.filter(user=user).first()
        data['company_address'] = buyer.company_address
        data['company_full_name'] = buyer.company_full_name
        data['phone'] = buyer.phone
        data['company_tax'] = buyer.company_tax
        data['user_type'] = 'Buyer'
    if user.isSupplier():
        supplier = Supplier.objects.filter(user=user).first()
        data['company_address'] = supplier.company_address
        data['company_full_name'] = supplier.company_full_name
        data['phone'] = supplier.phone
        data['company_tax'] = supplier.company_tax
        data['user_type'] = 'Supplier'
    data['tax'] = round(data['sub_total'] * 0.1, 2)

    data['total'] = float(data['sub_total']) + data['tax']
    data['tax'] = '{:20,.0f}'.format(data['tax'])

    for detail in data['detail_list']:
        detail['unit_price'] = '{:20,.0f}'.format(detail['unit_price'])
        detail['total_amount'] = '{:20,.0f}'.format(detail['total_amount'])
    p = inflect.engine()

    if data['is_topup']:
        data['total'] = data['sub_total']
        data['tax'] = ''
    data['sub_total'] = '{:20,.0f}'.format(data['sub_total'])
    language_code = user.language.item_code
    if language_code == "vi":
        data['total_string'] = covert_number_to_string(int(float(data['total']))).lstrip().capitalize()
        data['total'] = '{:20,.0f}'.format(data['total'])
        template = get_template("invoice_vi.html").render(data)
    else:
        data['total_string'] = p.number_to_words(round(data['total'])).capitalize() + " dong"
        data['total'] = '{:20,.0f}'.format(data['total'])
        template = get_template("invoice.html").render(data)

    options = {
        'page-size': 'A4',
        'margin-top': '9mm',
        'margin-right': '9mm',
        'margin-bottom': '9mm',
        'margin-left': '9mm',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }    
    
    file_name = f'''media/{data['user'].id}/{str(data['invoice_no'])}/draft_invoice.pdf'''
    Path(f'''media/{data['user'].id}/{str(data['invoice_no'])}''').mkdir(parents=True, exist_ok=True)
    pdf = pdfkit.from_string(template, file_name, options=options)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="{}'.format("draft_invoice.pdf")
    return response


# --------------------------------E_invoice--------------------------------
# Sandbox
URL = settings.EINVOICE_URL 
USERNAME = settings.EINVOICE_USERNAME
PASSWORD = settings.EINVOICE_PASSWORD

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r


def login():
    url_login = URL + "api/authenticate"
    values = {"username": USERNAME, "password": PASSWORD}
    print(values)
    response = requests.post(url_login, verify=False, data=json.dumps(values), headers={"content-type": "application/json"})
    print(json.loads(response.text))
    token = json.loads(response.text).get('id_token')
    return token


def customer_create(user):
    url_customer = URL + "api/customers"
    if user.isBuyer():
        body = {
            "address": user.buyer.company_address,
            "code": user.username,
            "customerType": None,
            "discount": 0,
            "email": user.email,
            "name": user.buyer.company_full_name,
            "buyerName": user.full_name,
            "phones": user.buyer.phone,
            "taxCode": user.buyer.company_tax,
        }
    elif user.isSupplier():
        body = {
            "address": user.supplier.company_address,
            "bankAccount": user.supplier.bank_account_number,
            "bankInfo": user.supplier.international_bank,
            "code": user.username,
            "customerType": None,
            "discount": 0,
            "email": user.email,
            "name": user.supplier.company_full_name,
            "buyerName": user.full_name,
            "phones": user.supplier.phone,
            "taxCode": user.supplier.company_tax,
        }
    customer_create = requests.post(url_customer, verify=False, data=json.dumps(body), headers={"content-type": "application/json"}, auth=BearerAuth(login()))
    return json.loads(customer_create.content.decode("utf-8"))


def customer_update(user, customer):
    url_customer = URL + "api/customers"
    if user.isBuyer():
        customer["address"] = user.buyer.company_address
        customer["code"] = user.username
        customer["customerType"] = None
        customer["email"] = user.email
        customer["name"] = user.buyer.company_full_name
        customer["buyerName"] = user.full_name
        customer["phones"] = user.buyer.phone
        customer["taxCode"] = user.buyer.company_tax
    elif user.isSupplier():
        customer["address"] = user.supplier.company_address
        customer["bankAccount"] = user.supplier.bank_account_number
        customer["bankInfo"] = user.supplier.international_bank
        customer["code"] = user.username
        customer["customerType"] = None
        customer["email"] = user.email
        customer["name"] = user.supplier.company_full_name
        customer["buyerName"] = user.full_name
        customer["phones"] = user.supplier.phone
        customer["taxCode"] = user.supplier.company_tax
    customer_update = requests.put(url_customer, verify=False, data=json.dumps(customer), headers={"content-type": "application/json"}, auth=BearerAuth(login()))
    return json.loads(customer_update.content.decode("utf-8"))


def get_customer(params):
    url_get_customer = URL + "api/customers/search"
    r = requests.get(url_get_customer, verify=False, auth=BearerAuth(login()), params=params)
    return json.loads(r.content.decode("utf-8"))


def bill_create(body):
    url_create_bill = URL + "api/bills"
    bill_create = requests.post(url_create_bill, verify=False, data=json.dumps(body), headers={"content-type": "application/json"}, auth=BearerAuth(login()))
    return {"status": bill_create.status_code, "message": json.loads(bill_create.content.decode("utf-8"))}


def dowload_bill(url, file_name):
    dowload_bill = requests.get(url, verify=False, headers={"content-type": "application/pdf"}, auth=BearerAuth(login()))
    x = json.loads(dowload_bill.content)
    with open(file_name, "w+b") as f:
        f.write(codecs.decode(x.get('pdfBase64').encode(), "base64"))
    return {"status": dowload_bill.status_code}


def sign_hms(bill_id):
    url_sign_hms = URL + "api/bills/sign-hsm"
    params = {"ids": bill_id}
    sign_hms = requests.get(url_sign_hms, verify=False, auth=BearerAuth(login()), params=params)
    return {"status": sign_hms.status_code}


class Invoice:
    def e_invoice(data):
        user = data.get('user')
        params = {"code": user.username}
        if len(get_customer(params)) == 0:
            customer = customer_create(user)
        else:
            customer = get_customer(params)[0]
            customer = customer_update(user, customer)
        # bill
        paymentType = {1: "CASH", 2: 'TRANSFER', 3: 'CASHTRANS', 4: 'CREDIT', 5: 'CLEARING', 6: 'TRANSFER_CLEARING', 7: 'DEBT_CLEARING'}
        taxRateId = {1: "10%", 2: "5%", 3: "0%", 4: "NO_Tax"}

        if data.get("deposit") is not None:
            taxAmount = data.get("deposit") * 0.1
            totalAmount = data.get("deposit")
        else:
            taxAmount = data.get('history').amount * 0.1
            totalAmount = data.get('history').amount
        body_bill = {
            "id": None,
            "paymentType": "TRANSFER",
            "multipleTaxRate": False,
            "createdDate": None,
            "lastModifiedDate": None,
            "customerId": customer.get('id'),
            "billTemplateId": 2561,
            "taxRateId": 1,
            "discount": data.get('discount'),
            "discountType": "DISCOUNT_RATE",
            "discountContent": data.get('discountContent'),
            "billEntries": data.get('product'),
            "billExtraFields": [],
            "clientSigned": False,
            "customerSigned": False,
            "taxAmount": taxAmount,
            "totalAmount": totalAmount,
            "billCurrency": "VND",
            "paymentCurrency": "VND",
            "exchangeRate": None,
            "billFees": [],
            "note": None,
            "hidePrice": False,
            "otherPaymentValue": "",
        }
        bill = bill_create(body_bill)
        bill_id = bill.get("message").get('id')
        sign_hms(bill_id=bill_id)
        file_name = f'''media/{user.id}/{str(data.get('history').order_no)}/invoice.pdf'''
        data.get('history').invoice_receipt = f'''{user.id}/{str(data.get('history').order_no)}/invoice.pdf'''
        data.get('history').save()
        Path(f'''media/{user.id}/{str(data.get('history').order_no)}''').mkdir(parents=True, exist_ok=True)
        url = URL + f'''api/bills/{bill_id}/pdf'''
        return dowload_bill(url, file_name)


# -----------------covert number to string-------------------
mNumText = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def read_dozens(number, daydu):
    result = ''
    dozens = number // 10
    unit = number % 10
    if dozens > 1:
        result = " " + mNumText[dozens] + " mươi"
        if unit == 1:
            result += " mốt"
    elif dozens == 1:
        result = " mười"
        if unit == 1:
            result += " một"
    elif daydu and unit > 0:
        result = " lẻ"

    if unit == 5 and dozens >= 1:
        result += " lăm"
    elif unit > 1 or (unit == 1 and dozens == 0):
        result += " " + mNumText[unit]
    return result


def read_hundreds(number, daydu):
    result = ""
    hundreds = number // 100
    number = number % 100
    if daydu or hundreds > 0:
        result = " " + mNumText[hundreds] + " trăm"
        result += read_dozens(number, True)
    else:
        result = " " + read_dozens(number, False)
    return result


def read_millions(number, daydu):
    result = ""
    millions = number // 1000000
    number = number % 1000000
    if millions > 0:
        result = " " + read_hundreds(millions, daydu) + " triệu"
        daydu = True
    thousand = number // 1000
    number = number % 1000
    if thousand > 0:
        result += read_hundreds(thousand, daydu) + " nghìn"
        daydu = True
    if number > 0:
        result += read_hundreds(number, daydu)
    return result


def covert_number_to_string(number):
    if number == 0:
        return mNumText[0]
    result = ""
    billion = number // 1000000000
    number = number % 1000000000
    while True:
        if billion > 0:
            result = read_millions(billion, False) + " tỷ" + result
            billion = number // 1000000000
        else:
            result = result + read_millions(number, False)
            break
    return result + " đồng"

