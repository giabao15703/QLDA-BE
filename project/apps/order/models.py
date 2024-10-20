from django.db import models
import random
import string
from enum import Enum
# from apps.payment.models import METHOD_PAYMENT_CHOICES, PAYMENT_STATUS_CHOICES
from apps.users.models import SupplierProduct, Buyer, Supplier
from apps.master_data.models import Currency, Country, CountryState
from apps.delivery.models import ShippingFee
from apps.master_data.models import Voucher
from apps.users.models import Buyer
from django.contrib.auth.hashers import make_password, check_password
# --------------------------------- Order ---------------------------------

class OrderType(Enum):
    KCS = 'KCS'
    WARRANTY = 'WARRANTY'

class OrderStatus(Enum):
    CART = 'CART'
    PENDING = 'PENDING'
    PAID = 'PAID'
    DELIVERING ='DELIVERING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

def generate_order_code():
    first_letter = random.choice(string.ascii_uppercase)
    seven_digits = ''.join(random.choice(string.digits) for _ in range(7))
    return first_letter + seven_digits

class Order(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='order_buyer')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='order_supplier', null=True, blank=True)
    order_type = models.CharField(max_length=10, choices=[(type.value, type.name.capitalize()) for type in OrderType])
    order_code = models.CharField(max_length=8, default=generate_order_code, unique=True)
    order_status = models.CharField(max_length=10, choices=[(status.value, status.name.capitalize()) for status in OrderStatus],default=OrderStatus.CART.value)
    tax_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    voucher_code_order = models.ForeignKey(Voucher, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(CountryState, on_delete=models.CASCADE, related_name='order_city', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # rating_product_quality = models.DecimalField(max_digits=2, decimal_places=1, default=0) 
    # rating_delivery_time = models.DecimalField(max_digits=2, decimal_places=1, default=0)  

    class Meta: 
        db_table = 'order'
  
# --------------------------------- Order Payment ---------------------------------

# class OrderPaymentDetails(models.Model):
#     order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='order_payment_details')
#     payment_method = models.PositiveSmallIntegerField(choices=METHOD_PAYMENT_CHOICES)
#     payment_status = models.PositiveSmallIntegerField(choices=PAYMENT_STATUS_CHOICES, null=False)
#     amount_paid = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta: 
#         db_table = 'order_payment_detail'

# --------------------------------- Order Addresses ---------------------------------

class OrderAddresses(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='order_addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255)
    country = models.OneToOneField(Country, on_delete=models.CASCADE, related_name='order_country')
    state = models.OneToOneField(CountryState, on_delete=models.CASCADE, related_name='order_state')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'order_addresses'

# --------------------------------- Order Items ---------------------------------

class OrderItems(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name='order_items')
    taxGTGT = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.IntegerField()
    # rating_product_quality = models.DecimalField(max_digits=2, decimal_places=1, default=0) 
    # rating_delivery_time = models.DecimalField(max_digits=2, decimal_places=1, default=0)  


    class Meta: 
        db_table = 'order_items'

# --------------------------------- Order Delivery ---------------------------------
class OrderDeliveryTimelines(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_delivery_timelines')
    time = models.CharField(max_length=255)
    order_date = models.DateTimeField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = 'order_delivery_timelines'

# --------------------------------- Order Delivery Shipping Fee ---------------------------------
class OrderDeliveryShippingFee(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='order_delivery_shipping_fee')
    delivery_shipping_fee = models.OneToOneField(ShippingFee, on_delete=models.CASCADE, related_name='order_delivery_shipping_fee')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'order_delivery_shipping_fee'

