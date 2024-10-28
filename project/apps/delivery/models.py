import random
from django.db import models
from apps.master_data.models import (
    CountryState,
)
from apps.users.models import User
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


class DeTai(models.Model):
    giang_vien = models.ForeignKey(User, on_delete=models.CASCADE)
    ten_de_tai = models.CharField(max_length=255)
    mo_ta = models.TextField()

    class Meta:
        db_table = 'detai'

    @property
    def giang_vien_full_name(self):
        return self.giang_vien.full_name



class GroupQLDA(models.Model):
    ma_Nhom = models.CharField(max_length=10, unique=True, default="")
    name = models.CharField(max_length=255)
    de_tai = models.CharField(max_length=1024)
    status = models.BooleanField(default=True)
    member_count = models.PositiveIntegerField(default=0)  # True là còn mở, False là đã đầy

    class Meta:
        db_table = 'group_qlda'
    def save(self, *args, **kwargs):
        if not self.ma_Nhom:
            # Tạo mã nhóm ngẫu nhiên và kiểm tra xem có trùng lặp không
            self.ma_Nhom = self.generate_unique_ma_nhom()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_ma_nhom():
        # Lặp lại việc tạo mã nhóm cho đến khi không trùng lặp
        while True:
            ma_nhom = f"DA{random.randint(100, 999)}"  # Tạo 3 số ngẫu nhiên
            if not GroupQLDA.objects.filter(ma_Nhom=ma_nhom).exists():  # Kiểm tra trùng lặp
                return ma_nhom

class JoinGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="join_groups")
    group = models.ForeignKey(GroupQLDA, on_delete=models.CASCADE, related_name="join_groups")
    
    class Meta:
        db_table = 'join_group'
        unique_together = ('user', 'group')
