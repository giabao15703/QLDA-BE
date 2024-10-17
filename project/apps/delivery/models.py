from django.db import models
from apps.master_data.models import (
    CountryState,
)
# Create your models here.
class ShippingFee(models.Model):
    pick_up_city = models.ForeignKey(CountryState, on_delete=models.CASCADE, related_name='pick_up_city')
    destination_city = models.ForeignKey(CountryState, on_delete=models.CASCADE, related_name='destination_city')
    weight = models.PositiveIntegerField(default=0)
    fee = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'delivery_shipping_fee'

class TransporterList(models.Model):
    short_name=models.CharField(max_length=255)
    long_name=models.CharField(max_length=255)
    code = models.CharField(max_length=6,unique=True)
    tax = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
    address = models.CharField(max_length=1024)
    email=models.CharField(max_length=255)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'delivery_transporter_list'

class DeliveryResponsible(models.Model):
    transporter_code = models.ForeignKey(TransporterList, on_delete=models.CASCADE, related_name='transporter_code')
    city_code = models.ForeignKey(CountryState, on_delete=models.CASCADE, related_name='city_code')
    effective_date = models.DateField()
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'delivery_delivery_responsible'