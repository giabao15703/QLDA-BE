import random
import uuid 
from django.db import models
from apps.master_data.models import (
    CountryState,
)
from apps.users.models import User, Admin
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
    idgvhuongdan = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name="huongdan_detai", null=True, blank=True)
    idgvphanbien = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name="phanbien_detai")
    idnhom = models.CharField(max_length=10, unique=True, null=True, blank=True)
    madoan = models.CharField(max_length=20, unique=True, null=True, blank=True)
    chuyennganh = models.CharField(max_length=100, null=True, blank=True)
    tendoan = models.CharField(max_length=255, null=True, blank=True)
    mota = models.TextField(null=True, blank=True)
    trangthai = models.CharField(max_length=20, default="0",null=True, blank=True)  # 0 là chưa duyệt
    yeucau = models.TextField(null=True, blank=True)
    idkehoach = models.ForeignKey('KeHoachDoAn', on_delete=models.CASCADE, default=1,null=True, blank=True)

    class Meta:
        db_table = 'detai'

    @staticmethod
    def generate_unique_madoan():
        """Tạo mã đồ án ngẫu nhiên và đảm bảo không trùng."""
        while True:
            ma_do_an = f"DA{uuid.uuid4().hex[:8].upper()}"
            if not DeTai.objects.filter(madoan=ma_do_an).exists():
                return ma_do_an

class GroupQLDA(models.Model):
    ma_Nhom = models.CharField(max_length=10, unique=True, default="")
    name = models.CharField(max_length=255)
    de_tai = models.ForeignKey(DeTai, on_delete=models.SET_NULL, null=True, blank=True, related_name="de_tai")
    status = models.BooleanField(default=True)
    member_count = models.PositiveIntegerField(default=0)
    max_member = models.PositiveIntegerField(default=5)
    leader_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_groups"
    )

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
    def get_users_in_group(self):
        return self.join_groups.all().values_list('user', flat=True)
class JoinGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="join_groups")
    group = models.ForeignKey(GroupQLDA, on_delete=models.CASCADE, related_name="join_groups")
    role = models.CharField(max_length=20, default="member")
    
    class Meta:
        db_table = 'join_group'
        unique_together = ('user', 'group')
    def get_users_in_group(self):
        return self.user.all()

from enum import Enum       
class RequestType(Enum):
    INVITE = 1
    JOIN_REQUEST = 2

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace("_", " ").title()) for item in cls]

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="join_requests")
    group = models.ForeignKey(GroupQLDA, on_delete=models.CASCADE, related_name="join_requests")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    leader_user_id = models.IntegerField(null=True, blank=True)
    request_type = models.CharField(
      choices=[("joinRequest", "Join Request"), ("invite", "Invite")],  # Sử dụng chuỗi cho request_type
      default="joinRequest",  # Mặc định là 'joinRequest'
      max_length=20
    )

    @staticmethod
    def get_group_leader_user_id(group_id):
        """Lấy userId của leader dựa trên group_id từ bảng JoinGroup."""
        leader = JoinGroup.objects.filter(group_id=group_id, role="leader").first()
        return leader.user.id if leader else None

    def save(self, *args, **kwargs):
        if not self.leader_user_id:
            leader_user_id = self.get_group_leader_user_id(self.group.id)
            if leader_user_id:
                self.leader_user_id = leader_user_id
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'join_request'
        unique_together = ('user', 'group')

class KeHoachDoAn(models.Model):
    sl_sinh_vien = models.IntegerField()  # Số lượng sinh viên
    sl_do_an = models.IntegerField()  # Số lượng đồ án
    ky_mo = models.CharField(max_length=50)  # Kỳ mở của đồ án

    tgbd_do_an = models.DateTimeField()  # Thời gian bắt đầu đồ án
    tgkt_do_an = models.DateTimeField()  # Thời gian kết thúc đồ án

    tgbd_tao_do_an = models.DateTimeField()  # Thời gian bắt đầu tạo đồ án
    tgkt_tao_do_an = models.DateTimeField()  # Thời gian kết thúc tạo đồ án

    tgbd_dang_ky_de_tai = models.DateTimeField()  # Thời gian bắt đầu đăng ký đề tài
    tgkt_dang_ky_de_tai = models.DateTimeField()  # Thời gian kết thúc đăng ký đề tài

    tgbd_lam_do_an = models.DateTimeField()  # Thời gian bắt đầu làm đồ án
    tgkt_lam_do_an = models.DateTimeField()  # Thời gian kết thúc làm đồ án

    tgbd_cham_phan_bien = models.DateTimeField()  # Thời gian bắt đầu chấm phản biện
    tgkt_cham_phan_bien = models.DateTimeField()  # Thời gian kết thúc chấm phản biện

    tgbd_cham_hoi_dong = models.DateTimeField()  # Thời gian bắt đầu chấm hội đồng
    tgkt_cham_hoi_dong = models.DateTimeField()  # Thời gian kết thúc chấm hội đồng

    class Meta:
        db_table = 'kehoach_doan'

    def save(self, *args, **kwargs):
        # Kiểm tra trùng lặp thời gian như đã làm ở bước trước nếu cần
        super().save(*args, **kwargs)

class Notification(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField() 
    created_date = models.DateTimeField(auto_now_add=True)  # Ngày tạo thông báo
    status = models.BooleanField(default=True)  # Trạng thái thông báo (True: hoạt động, False: không hoạt động)

    class Meta:
        db_table = 'notification'

    def __str__(self):
        return self.title


class Grading(models.Model):
    detai = models.ForeignKey(DeTai, on_delete=models.CASCADE, related_name='gradings')
    group = models.ForeignKey(GroupQLDA, on_delete=models.CASCADE, related_name='gradings')
    diem_huongdan = models.FloatField(default=0.0)
    diem_phanbien = models.FloatField(default=0.0)

    class Meta:
        db_table = 'grading'
