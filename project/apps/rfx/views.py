import pdfkit
from apps.users.models import Buyer, Supplier
from django.http import HttpResponse
from django.template.loader import get_template
from pathlib import Path

def generate_contract(data):
    data = data
    user_buyer = data['buyer']
    user_supplier = data['supplier']
    if user_buyer.isBuyer():
        buyer = Buyer.objects.filter(user=user_buyer).first()
        data['buyer_code'] = buyer.user.username
        data['buyer_company_name'] = buyer.company_full_name
        data['buyer_company_address'] = buyer.company_address
        data['buyer_name'] = buyer.user.full_name
        data['buyer_telephone'] = buyer.phone
        data['buyer_mobile'] = buyer.phone
        data['buyer_email'] = buyer.company_email
    if user_supplier.isSupplier():
        supplier = Supplier.objects.filter(user=user_supplier).first()
        data['supplier_code'] = supplier.user.username
        data['supplier_company_name'] = supplier.company_full_name
        data['supplier_company_address'] = supplier.company_address
        data['supplier_name'] = supplier.user.full_name
        data['supplier_email'] = supplier.user.email
        data['supplier_telephone'] = supplier.phone
        data['supplier_mobile'] = supplier.phone

    for item in data['item_list']:
        if item['unit_price'] is not None:
            item['unit_price'] = '{:20,.0f}'.format(item['unit_price'])

    template = get_template("contract.html").render(data)

    file_name = f'''media/{data['buyer'].id}/{str(data['item_code'])}/po_contract.pdf'''
    Path(f'''media/{data['buyer'].id}/{str(data['item_code'])}''').mkdir(parents=True, exist_ok=True)

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
    pdf = pdfkit.from_string(template, file_name, options=options)
    return HttpResponse(pdf, content_type='application/pdf')

def generate_pdf(data, template_file_name, file_name, path):
    template = get_template(template_file_name).render(data)

    file_name = f'''media/{path}/{file_name}'''
    Path(f'''media/{path}''').mkdir(parents=True, exist_ok=True)

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
    pdf = pdfkit.from_string(template, file_name, options=options)
    return pdf
    