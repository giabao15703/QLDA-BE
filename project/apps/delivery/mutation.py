import datetime
import filetype
import graphene
import re
import random
from graphene import relay 
from django.db.models import Subquery
from graphene_django import DjangoObjectType
from django.utils import timezone
from apps.delivery.schema import (
    GradingNode,
    NotificationNode,
    ShippingFeeNode,
    TransporterListNode,
    DeliveryResponsibleNode,
    GetToken,
    DeTaiNode,
    GroupQLDANode,
    KeHoachDoAnNode,

)
from apps.users.models import Token
from apps.delivery.models import (
    Grading,
    Notification,
    ShippingFee,
    TransporterList,
    DeliveryResponsible,
    DeTai,
    GroupQLDA,
    JoinGroup,
    JoinRequest,
    User,
    Admin,
    KeHoachDoAn,
    RequestType
)

from apps.delivery.error_code import (
    DeliveryError
)
from apps.master_data.models import (
    CountryState
)
from apps.payment.models import UserPayment
from apps.sale_schema.models import ProfileFeaturesBuyer, ProfileFeaturesSupplier, SICPRegistration
from apps.payment.schema import send_mail_upgraded, send_mail_sicp
from apps.users.error_code import UserError
from apps.core import Error
from django.core.mail import send_mail
from django.db import transaction
from graphene_django_plus.mutations import ModelUpdateMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from django.core.exceptions import ValidationError

class ShippingFeeInput(graphene.InputObjectType):
    pick_up_city_code = graphene.String(required=True)
    destination_city_code = graphene.String(required=True)
    weight = graphene.Int(required=True, default_value=0)
    fee = graphene.Decimal(required=True, default_value=0)
    status = graphene.Boolean(required=True, default_value=True)


class ShippingFeeCreate(graphene.Mutation):
    class Arguments:
        input = ShippingFeeInput(required=True)

    status = graphene.Boolean()
    shipping_fee = graphene.Field(ShippingFeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():
                if input.weight < 0:
                    error = Error(code="DELIVERY_05", message=DeliveryError.DELIVERY_05)
                    return ShippingFeeCreate(status=False, error=error)
                if input.fee < 0:
                    error = Error(code="DELIVERY_05", message=DeliveryError.DELIVERY_05)
                    return ShippingFeeCreate(status=False, error=error)
                pick_up_city = CountryState.objects.filter(id=input.pick_up_city_code).first()
                if pick_up_city is None:
                    error = Error(code="DELIVERY_03", message=DeliveryError.DELIVERY_03)
                    return ShippingFeeCreate(status=False, error=error)
                destinaotion_city = CountryState.objects.filter(id=input.destination_city_code).first()
                if destinaotion_city is None:
                    error = Error(code="DELIVERY_04", message=DeliveryError.DELIVERY_04)
                    return ShippingFeeCreate(status=False, error=error)
                try:
                    shippingfee = ShippingFee.objects.create(
                        pick_up_city_id = input.pick_up_city_code,
                        destination_city_id = input.destination_city_code,
                        weight = input.weight,
                        fee = input.fee,
                        status = input.status,
                    )
                    return ShippingFeeCreate(status=True, shipping_fee=shippingfee)
                except:
                    transaction.set_rollback(True)
                    error = Error(code="DELIVERY_06", message=DeliveryError.DELIVERY_06)
                    return ShippingFeeCreate(status=False, error=error)
            else:
                error = Error(code="DELIVERY_01", message=DeliveryError.DELIVERY_01)
                return ShippingFeeCreate(error=error, status=False)
        except:
            error = Error(code="DELIVERY_02", message=DeliveryError.DELIVERY_02)
            return ShippingFeeCreate(error=error, status=False)

class ShippingFeeUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = ShippingFeeInput(required=True)

    status = graphene.Boolean()
    shipping_fee = graphene.Field(ShippingFeeNode)
    error = graphene.Field(Error)

    def mutate(root, info, input, id):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():
                try:
                    shippingfee = ShippingFee.objects.get(id=id)
                    if input.weight < 0:
                        error = Error(code="DELIVERY_05", message=DeliveryError.DELIVERY_05)
                        return ShippingFeeUpdate(status=False, error=error)
                    if input.fee < 0:
                        error = Error(code="DELIVERY_05", message=DeliveryError.DELIVERY_05)
                        return ShippingFeeUpdate(status=False, error=error)
                    pick_up_city = CountryState.objects.filter(id=input.pick_up_city_code).first()
                    if pick_up_city is None:
                        error = Error(code="DELIVERY_03", message=DeliveryError.DELIVERY_03)
                        return ShippingFeeUpdate(status=False, error=error)
                    destinaotion_city = CountryState.objects.filter(id=input.destination_city_code).first()
                    if destinaotion_city is None:
                        error = Error(code="DELIVERY_04", message=DeliveryError.DELIVERY_04)
                        return ShippingFeeUpdate(status=False, error=error)
                    shippingfee.pick_up_city_id = input.pick_up_city_code
                    shippingfee.destination_city_id = input.destination_city_code
                    shippingfee.weight = input.weight
                    shippingfee.fee = input.fee
                    shippingfee.status = input.status
                    shippingfee.save()
                    return ShippingFeeUpdate(status=True, shipping_fee=shippingfee)
                except:
                    transaction.set_rollback(True)
                    error = Error(code="DELIVERY_07", message=DeliveryError.DELIVERY_07)
                    return ShippingFeeUpdate(status=False, error=error)
            else:
                error = Error(code="DELIVERY_01", message=DeliveryError.DELIVERY_01)
                return ShippingFeeUpdate(error=error, status=False)
        except:
            error = Error(code="DELIVERY_02", message=DeliveryError.DELIVERY_02)
            return ShippingFeeUpdate(error=error, status=False)

class ShippingFeeDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        try:
            shippingFee = ShippingFee.objects.get(pk=id)
            shippingFee.delete()
            return ShippingFeeDelete(status=True)
        except Exception as err:
            error = Error(code="DELIVERY_07", message=DeliveryError.DELIVERY_07)
            return ShippingFeeDelete(status=False, error=error)

class TransporterListInput(graphene.InputObjectType):
    short_name = graphene.String(required=True)
    long_name = graphene.String(required=True)
    code = graphene.String(required=True)
    tax = graphene.String(required=True)
    address = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=True)
    status = graphene.Boolean(required=True, default_value=True)

class TransporterListCreate(graphene.Mutation):
    class Arguments:
        input = TransporterListInput(required=True)

    status = graphene.Boolean()
    transporter_list = graphene.Field(TransporterListNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():
                if len(input.code) != 6:
                    error = Error(code="DELIVERY_08", message=DeliveryError.DELIVERY_08)
                    return TransporterListCreate(status=False, error=error)
                
                try:
                    transporter = TransporterList.objects.create(
                        short_name = input.short_name,
                        long_name = input.long_name,
                        code = input.code,
                        tax = input.tax,
                        address = input.address,
                        email = input.email,
                        phone = input.phone,
                        status = input.status,
                    )
                    return TransporterListCreate(status=True, transporter_list=transporter)
                except:
                    transaction.set_rollback(True)
                    error = Error(code="DELIVERY_09", message=DeliveryError.DELIVERY_09)
                    return TransporterListCreate(status=False, error=error)
            else:
                error = Error(code="DELIVERY_01", message=DeliveryError.DELIVERY_01)
                return TransporterListCreate(error=error, status=False)
        except:
            error = Error(code="DELIVERY_02", message=DeliveryError.DELIVERY_02)
            return TransporterListCreate(error=error, status=False)

class TransporterListUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = TransporterListInput(required=True)

    status = graphene.Boolean()
    transporter_list = graphene.Field(TransporterListNode)
    error = graphene.Field(Error)

    def mutate(root, info, input, id):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():
                try:
                    transporter = TransporterList.objects.get(id=id)
                    if len(input.code) != 6:
                        error = Error(code="DELIVERY_08", message=DeliveryError.DELIVERY_08)
                        return TransporterListUpdate(status=False, error=error)
                    
                    transporter.short_name = input.short_name
                    transporter.long_name = input.long_name
                    transporter.code = input.code
                    transporter.tax = input.tax
                    transporter.address = input.address
                    transporter.email = input.email
                    transporter.phone = input.phone
                    transporter.status = input.status
                    transporter.save()
                    return TransporterListUpdate(status=True, transporter_list=transporter)
                except:
                    transaction.set_rollback(True)
                    error = Error(code="DELIVERY_07", message=DeliveryError.DELIVERY_07)
                    return TransporterListUpdate(status=False, error=error)
            else:
                error = Error(code="DELIVERY_01", message=DeliveryError.DELIVERY_01)
                return TransporterListUpdate(error=error, status=False)
        except:
            error = Error(code="DELIVERY_02", message=DeliveryError.DELIVERY_02)
            return TransporterListUpdate(error=error, status=False)

class TransporterListDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        try:
            transporter = TransporterList.objects.get(pk=id)
            transporter.delete()
            return TransporterListDelete(status=True)
        except Exception as err:
            error = Error(code="DELIVERY_10", message=DeliveryError.DELIVERY_10)
            return TransporterListDelete(status=False, error=error)

class DeliveryResponsibleInput(graphene.InputObjectType):
    transporter_code = graphene.String(required=True)
    city_code = graphene.String(required=True)
    effective_date = graphene.Date(required=True)
    status = graphene.Boolean(required=True, default_value=True)


class DeliveryResponsibleCreate(graphene.Mutation):
    class Arguments:
        input = DeliveryResponsibleInput(required=True)

    status = graphene.Boolean()
    delivery_responsible = graphene.Field(DeliveryResponsibleNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():
                transporter_code = TransporterList.objects.filter(id=input.transporter_code).first()
                if transporter_code is None:
                    error = Error(code="DELIVERY_10", message=DeliveryError.DELIVERY_10)
                    return DeliveryResponsibleCreate(status=False, error=error)
                city_code = CountryState.objects.filter(id=input.city_code).first()
                if city_code is None:
                    error = Error(code="DELIVERY_11", message=DeliveryError.DELIVERY_11)
                    return DeliveryResponsibleCreate(status=False, error=error)
                try:
                    delivery_responsible = DeliveryResponsible.objects.create(
                        transporter_code_id = input.transporter_code,
                        city_code_id = input.city_code,
                        effective_date = input.effective_date,
                        status = input.status,
                    )
                    return DeliveryResponsibleCreate(status=True, delivery_responsible=delivery_responsible)
                except:
                    transaction.set_rollback(True)
                    error = Error(code="DELIVERY_12", message=DeliveryError.DELIVERY_12)
                    return DeliveryResponsibleCreate(status=False, error=error)
            else:
                error = Error(code="DELIVERY_01", message=DeliveryError.DELIVERY_01)
                return DeliveryResponsibleCreate(error=error, status=False)
        except:
            error = Error(code="DELIVERY_02", message=DeliveryError.DELIVERY_02)
            return DeliveryResponsibleCreate(error=error, status=False)

class DeliveryResponsibleUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = DeliveryResponsibleInput(required=True)

    status = graphene.Boolean()
    delivery_responsible = graphene.Field(DeliveryResponsibleNode)
    error = graphene.Field(Error)

    def mutate(root, info, input, id):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():
                try:
                    delivery_responsible = DeliveryResponsible.objects.get(pk=id)
                    transporter_code = TransporterList.objects.filter(id=input.transporter_code).first()
                    if transporter_code is None:
                        error = Error(code="DELIVERY_10", message=DeliveryError.DELIVERY_10)
                        return DeliveryResponsibleUpdate(status=False, error=error)
                    city_code = CountryState.objects.filter(id=input.city_code).first()
                    if city_code is None:
                        error = Error(code="DELIVERY_11", message=DeliveryError.DELIVERY_11)
                        return DeliveryResponsibleUpdate(status=False, error=error)
                    
                    delivery_responsible.transporter_code_id = input.transporter_code
                    delivery_responsible.city_code_id = input.city_code
                    delivery_responsible.effective_date = input.effective_date
                    delivery_responsible.status = input.status
                    delivery_responsible.save()
                    return DeliveryResponsibleUpdate(status=True, delivery_responsible=delivery_responsible)
                except Exception as err:
                    print({"exeption": err})
                    transaction.set_rollback(True)
                    error = Error(code="DELIVERY_13", message=DeliveryError.DELIVERY_13)
                    return DeliveryResponsibleUpdate(status=False, error=error)
            else:
                error = Error(code="DELIVERY_01", message=DeliveryError.DELIVERY_01)
                return DeliveryResponsibleUpdate(error=error, status=False)
        except:
            error = Error(code="DELIVERY_02", message=DeliveryError.DELIVERY_02)
            return DeliveryResponsibleUpdate(error=error, status=False)

class DeliveryResponsibleDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id, **kwargs):
        try:
            delivery_responsible = DeliveryResponsible.objects.get(pk=id)
            delivery_responsible.delete()
            return DeliveryResponsibleDelete(status=True)
        except Exception as err:
            error = Error(code="DELIVERY_13", message=DeliveryError.DELIVERY_13)
            return DeliveryResponsibleDelete(status=False, error=error)

class DeTaiInput(graphene.InputObjectType):
    #idgvhuongdan = graphene.ID(required=True)  # ID của giảng viên hướng dẫn
    tendoan = graphene.String(required=True)
    mota = graphene.String(required=True)

class DeTaiCreate(graphene.Mutation):
    class Arguments:
        input = DeTaiInput(required=True)

    status = graphene.Boolean()
    de_tai = graphene.Field(DeTaiNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            # Lấy giảng viên dựa trên ID
            token_key = GetToken.getToken(info)
            token = Token.objects.get(key=token_key)
            user = token.user
            if user.isAdmin():
                giang_vien = Admin.objects.get(user=user)
                # Lấy kế hoạch đồ án hợp lệ
                now = timezone.now().date()
                ke_hoach_do_an = KeHoachDoAn.objects.filter(
                    tgbd_tao_do_an__lte=now,
                    tgkt_tao_do_an__gte=now
                ).first()
                count = DeTai.objects.filter(idgvhuongdan=giang_vien, idkehoach=ke_hoach_do_an).count()

                if not ke_hoach_do_an:
                    error = Error(code="NO_VALID_KEHOACH", message="Không có kế hoạch đồ án nào trong thời gian cho phép tạo đề tài.")
                    return DeTaiCreate(status=False, error=error)
                # Lấy chuyên ngành từ giảng viên hoặc đặt giá trị mặc định
                chuyennganh = getattr(giang_vien, 'chuyen_nganh', 'Chưa xác định')

                # Tạo đề tài với các thuộc tính được yêu cầu
                de_tai = DeTai.objects.create(
                    idgvhuongdan=giang_vien,
                    idkehoach=ke_hoach_do_an,
                    tendoan=input.tendoan,
                    mota=input.mota,
                    madoan=DeTai.generate_unique_madoan(),
                    chuyennganh=chuyennganh,  # Lấy chuyên ngành từ giảng viên hoặc giá trị mặc định
                    trangthai="0"  # Đặt trạng thái mặc định là "0" (chưa duyệt)
                )
                return DeTaiCreate(status=True, de_tai=de_tai)

        except Admin.DoesNotExist:
            error = Error(code="NOT_FOUND", message="Giảng viên không tồn tại")
            return DeTaiCreate(status=False, error=error)
        except KeHoachDoAn.DoesNotExist:
            error = Error(code="NOT_FOUND", message="Kế hoạch đồ án không tồn tại")
            return DeTaiCreate(status=False, error=error)
        except Exception as e:
            error = Error(code="CREATE_ERROR", message=str(e))
            return DeTaiCreate(status=False, error=error)


class DeTaiUpdateInput(graphene.InputObjectType):
    tendoan = graphene.String()
    mota = graphene.String()
    trangthai = graphene.String() 
    yeucau = graphene.String()     
    idgvphanbienScalar = graphene.String()


class DeTaiUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = DeTaiUpdateInput(required=True)

    status = graphene.Boolean()
    de_tai = graphene.Field(DeTaiNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            # Lấy token từ context
            token_key = GetToken.getToken(info)
            token = Token.objects.get(key=token_key)
            user = token.user

            if user:
                # Lấy đề tài cần cập nhật
                de_tai = DeTai.objects.get(id=id)
                # Kiểm tra user_type
                if user.user_type == 1:  # Admin
                    # Kiểm tra sự tồn tại của Admin cho user
                    giang_vien = Admin.objects.filter(user=user).first()
                    
                    if not giang_vien:
                        error = Error(code="NOT_FOUND", message="Không tìm thấy Admin cho người dùng này.")
                        return DeTaiUpdate(status=False, error=error)
                    
                    if giang_vien.role == 4 or giang_vien.id == de_tai.idgvhuongdan.id:
                        # Cập nhật thông tin đề tài cho Admin
                        if input.tendoan is not None:
                            de_tai.tendoan = input.tendoan
                        if input.mota is not None:
                            de_tai.mota = input.mota
                        if giang_vien.role == 4:
                            if input.trangthai is not None:
                                de_tai.trangthai = input.trangthai
                            if input.yeucau is not None:
                                de_tai.yeucau = input.yeucau
                            if input.idgvphanbienScalar is not None:
                                gv_phan_bien = Admin.objects.filter(pk=input.idgvphanbienScalar).first()
                                if input.idgvphanbienScalar == "-1":
                                    de_tai.idgvphanbien = None
                                else:
                                    de_tai.idgvphanbien = gv_phan_bien
                    else:
                        error = Error(code="PERMISSION_DENIED", message="Bạn không có quyền cập nhật đề tài này.")
                        return DeTaiUpdate(status=False, error=error)

                elif user.user_type == 2:  # Sinh viên
                    # Kiểm tra xem user có phải là leader của nhóm trong join_group
                    join_group = JoinGroup.objects.filter(user=user, role="leader").first()

                    if not join_group:
                        error = Error(code="PERMISSION_DENIED", message="Bạn không phải là nhóm trưởng hoặc chưa tham gia nhóm.")
                        return DeTaiUpdate(status=False, error=error)

                    # Kiểm tra xem nhóm của user đã có đề tài chưa
                    if DeTai.objects.filter(idnhom=join_group.group.ma_Nhom).exists():
                        error = Error(code="ALREADY_REGISTERED", message="Nhóm của bạn đã đăng ký đề tài khác.")
                        return DeTaiUpdate(status=False, error=error)

                    # Cập nhật thông tin nếu là leader và nhóm chưa đăng ký đề tài
                    de_tai.idnhom = join_group.group.ma_Nhom
                    join_group.group.de_tai = de_tai

                # Lưu lại thay đổi
                de_tai.save()
                if user.user_type == 2 and join_group:
                    join_group.group.save()  # Nếu có thay đổi nhóm

                return DeTaiUpdate(status=True, de_tai=de_tai)

            else:
                error = Error(code="AUTHENTICATION_REQUIRED", message="Bạn cần đăng nhập để thực hiện thao tác này.")
                return DeTaiUpdate(status=False, error=error)

        except DeTai.DoesNotExist:
            error = Error(code="NOT_FOUND", message="Đề tài không tồn tại")
            return DeTaiUpdate(status=False, error=error)
        except Token.DoesNotExist:
            error = Error(code="AUTHENTICATION_REQUIRED", message="Token không hợp lệ hoặc đã hết hạn.")
            return DeTaiUpdate(status=False, error=error)
        except Exception as e:
            error = Error(code="UPDATE_ERROR", message=str(e))
            return DeTaiUpdate(status=False, error=error)


class DeTaiDelete(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, id):
        try:
            # Lấy đối tượng đề tài cần xoá
            de_tai = DeTai.objects.get(id=id)
            user = info.context.user

            # Kiểm tra quyền hạn: chỉ cho phép Trưởng khoa xoá
            if user.role != "1":  # Giả sử "1 - TruongKhoa" là vai trò của Trưởng khoa
                error = Error(code="PERMISSION_DENIED", message="Bạn không có quyền xoá đề tài này.")
                return DeTaiDelete(status=False, error=error)

            # Kiểm tra thời gian: chỉ cho phép xoá trong thời gian tạo đồ án
            now = timezone.now().date()
            if not (de_tai.idkehoach.tgbd_tao_do_an <= now <= de_tai.idkehoach.tgkt_tao_do_an):
                error = Error(code="TIME_CONSTRAINT", message="Đề tài chỉ có thể bị xoá trong thời gian tạo đồ án.")
                return DeTaiDelete(status=False, error=error)

            # Xoá đề tài
            de_tai.delete()
            return DeTaiDelete(status=True)

        except DeTai.DoesNotExist:
            error = Error(code="NOT_FOUND", message="Đề tài không tồn tại")
            return DeTaiDelete(status=False, error=error)
        except Exception as e:
            error = Error(code="DELETE_ERROR", message=str(e))
            return DeTaiDelete(status=False, error=error)


class GroupQLDAInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    

class GroupQLDACreate(graphene.Mutation):
    class Arguments:
        input = GroupQLDAInput(required=True)

    status = graphene.Boolean()
    group_qlda = graphene.Field(GroupQLDANode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
            user_creating_group = token.user

            #kiểm tra xem có kế hoạch đồ án nào đang mở đăng kí nhóm không
            now = timezone.now()
            ke_hoach_do_an = KeHoachDoAn.objects.filter(
                tgbd_dang_ky_de_tai__lte=now,
                tgkt_dang_ky_de_tai__gte=now
            ).first()

            if not ke_hoach_do_an:
                return GroupQLDACreate(
                    status=False,
                    error=Error(
                        code="NO_VALID_KEHOACH",
                        message=f"Không có kế hoạch đồ án nào trong thời gian cho phép tạo nhóm. Thời gian hiện tại: {now}."
                    )
                )

            sl_sinh_vien = ke_hoach_do_an.sl_sinh_vien
            

            if user_creating_group.isAdmin():
                return GroupQLDACreate(
                    status=False,
                    error=Error(
                        code="PERMISSION_DENIED",
                        message="Admin không thể tạo nhóm."
                    )
                )

            existing_group = JoinGroup.objects.filter(user=user_creating_group).first()
        
            if existing_group:
                return GroupQLDACreate(
                    status=False,
                    error=Error(
                        code="ALREADY_HAS_GROUP",
                        message=f"Người dùng đã tham gia nhóm {existing_group.group.name} trước đó."
                    )
                )

            group_qlda = GroupQLDA(
                name=input.name,
                leader_user=user_creating_group,  # Set leader_user to the user creating the group
                max_member = sl_sinh_vien
            )
            group_qlda.save()
            JoinGroup.objects.create(user=user_creating_group, group=group_qlda, role="leader")
            group_qlda.member_count += 1
            group_qlda.save()
            return GroupQLDACreate(status=True, group_qlda=group_qlda)
        except Exception as e:
            return GroupQLDACreate(
                status=False,
                error=Error(
                    code="CREATE_ERROR",
                    message="CREATE ERROR"
                )
            )

class GroupQLDAJoin(graphene.Mutation):
    class Arguments:
        group_id = graphene.ID(required=True)
        request_type = graphene.String(required=False)  # request_type là chuỗi

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(self, info, group_id, request_type=None):
        try:
            # Lấy thông tin người dùng từ token
            token = GetToken.getToken(info)
            user = token.user

            # Tìm nhóm dựa trên group_id
            group_qlda = GroupQLDA.objects.get(pk=group_id)

            # Kiểm tra nếu người dùng đã tham gia nhóm
            existing_group = JoinGroup.objects.filter(user=user, group=group_qlda).first()
            if existing_group:
                return GroupQLDAJoin(
                    status=False,
                    error=Error(
                        code="ALREADY_IN_GROUP",
                        message=f"Người dùng đã tham gia nhóm {existing_group.group.name} trước đó."
                    )
                )

            # Gán thẳng 'joinRequest' nếu không có giá trị từ client
            if not request_type:
                request_type = "joinRequest"  # Gán 'joinRequest' nếu không có giá trị

            # Ánh xạ chuỗi 'joinRequest' và 'invite' thành giá trị số tương ứng
            if request_type == "joinRequest":
                request_type = RequestType.JOIN_REQUEST.value  # Gán giá trị 2
            elif request_type == "invite":
                request_type = RequestType.INVITE.value  # Gán giá trị 1
            else:
                return GroupQLDAJoin(
                    status=False,
                    error=Error(
                        code="INVALID_REQUEST_TYPE",
                        message="Loại yêu cầu không hợp lệ."
                    )
                )

            # Kiểm tra nếu yêu cầu đã tồn tại và chưa được duyệt
            if JoinRequest.objects.filter(user=user, group=group_qlda, request_type=request_type, is_approved=False).exists():
                return GroupQLDAJoin(
                    status=False,
                    error=Error(
                        code="REQUEST_ALREADY_SENT",
                        message="Yêu cầu tham gia đã được gửi trước đó và đang chờ xử lý."
                    )
                )

            # Tạo yêu cầu tham gia nhóm
            JoinRequest.objects.create(user=user, group=group_qlda, request_type=request_type)

            return GroupQLDAJoin(status=True)

        except GroupQLDA.DoesNotExist:
            return GroupQLDAJoin(
                status=False,
                error=Error(
                    code="GROUP_NOT_FOUND",
                    message="Nhóm không tồn tại."
                )
            )
        except Exception as e:
            return GroupQLDAJoin(
                status=False,
                error=Error(
                    code="JOIN_ERROR",
                    message=str(e)
                )
            )



class AcceptJoinRequest(graphene.Mutation):
    class Arguments:
        join_request_id = graphene.ID(required=True)
    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, join_request_id):
        try:
            # Lấy yêu cầu tham gia dựa trên ID
            join_request = JoinRequest.objects.select_related('group', 'user').get(pk=join_request_id)

            # Kiểm tra nếu user hiện tại là leader của nhóm
            group = join_request.group
            leader_record = group.join_groups.filter(role="leader").first()
            if group.member_count >= group.max_member:
                return AcceptJoinRequest(
                    status=False,
                    error=Error(code="GROUP_FULL", message="Nhóm đã đủ số lượng thành viên.")
                )

            # Thêm người dùng vào nhóm với vai trò thành viên
            JoinGroup.objects.create(user=join_request.user, group=group, role="member")

            # Tăng số lượng thành viên trong nhóm
            group.member_count += 1
            group.save()

            # Xóa yêu cầu sau khi xử lý
            #if group.member_count >= group.max_member:
            #    JoinRequest.objects.filter(group=group).delete()
            #else:
            join_request.delete()

            # Gửi thông báo tới leader về việc chấp nhận yêu cầu
            if hasattr(leader_record.user, "send_notification"):
                leader_record.user.send_notification(
                    f"Yêu cầu của {join_request.user.email} đã được chấp nhận và thêm vào nhóm {group.name}."
                )

            return AcceptJoinRequest(status=True)

        except JoinRequest.DoesNotExist:
            return AcceptJoinRequest(
                status=False,
                error=Error(code="REQUEST_NOT_FOUND", message="Yêu cầu tham gia không tồn tại.")
            )
        except Exception as e:
            return AcceptJoinRequest(
                status=False,
                error=Error(code="ACCEPT_ERROR", message=str(e))
            )



""" class KeHoachDoAnType(DjangoObjectType):
    class Meta:
        model = KeHoachDoAn
        fields = "__all__"
        interfaces = (relay.Node,) """

class KeHoachDoAnInput(graphene.InputObjectType):
    sl_sinh_vien = graphene.Int(required=True)
    sl_do_an = graphene.Int(required=True)
    ky_mo = graphene.String(required=True)
    tgbd_do_an = graphene.DateTime(required=True)
    tgkt_do_an = graphene.DateTime(required=True)
    tgbd_tao_do_an = graphene.DateTime(required=True)
    tgkt_tao_do_an = graphene.DateTime(required=True)
    tgbd_dang_ky_de_tai = graphene.DateTime(required=True)
    tgkt_dang_ky_de_tai = graphene.DateTime(required=True)
    tgbd_lam_do_an = graphene.DateTime(required=True)
    tgkt_lam_do_an = graphene.DateTime(required=True)
    tgbd_cham_phan_bien = graphene.DateTime(required=True)
    tgkt_cham_phan_bien = graphene.DateTime(required=True)
    tgbd_cham_hoi_dong = graphene.DateTime(required=True)
    tgkt_cham_hoi_dong = graphene.DateTime(required=True)

import graphene

class CreateKeHoachDoAn(graphene.Mutation):
    class Arguments:
        input = KeHoachDoAnInput(required=True)

    status = graphene.Boolean()
    ke_hoach_do_an = graphene.Field(KeHoachDoAnNode)
    error = graphene.Field(Error)

    @staticmethod
    def validate_time_fields(input_data):
        """
        Kiểm tra tính hợp lệ của các trường thời gian dựa trên timeline yêu cầu:
        tgbd_do_an <= tgbd_tao_do_an <= tgkt_tao_do_an <= tgbd_dang_ky_de_tai <= tgkt_dang_ky_de_tai <=
        tgbd_lam_do_an <= tgkt_lam_do_an <= tgbd_cham_phan_bien <= tgkt_cham_phan_bien <= 
        tgbd_cham_hoi_dong <= tgkt_cham_hoi_dong <= tgkt_do_an
        """
        
        # Kiểm tra bao gồm tổng thể khoảng thời gian
        tgbd_do_an = input_data.tgbd_do_an
        tgkt_do_an = input_data.tgkt_do_an

        if not all([
            tgbd_do_an < input_data.tgbd_tao_do_an < tgkt_do_an,
            tgbd_do_an < input_data.tgkt_tao_do_an < tgkt_do_an,
            tgbd_do_an < input_data.tgbd_dang_ky_de_tai < tgkt_do_an,
            tgbd_do_an < input_data.tgkt_dang_ky_de_tai < tgkt_do_an,
            tgbd_do_an < input_data.tgbd_lam_do_an < tgkt_do_an,
            tgbd_do_an < input_data.tgkt_lam_do_an < tgkt_do_an,
            tgbd_do_an < input_data.tgbd_cham_phan_bien < tgkt_do_an,
            tgbd_do_an < input_data.tgkt_cham_phan_bien < tgkt_do_an,
            tgbd_do_an < input_data.tgbd_cham_hoi_dong < tgkt_do_an,
            tgbd_do_an < input_data.tgkt_cham_hoi_dong < tgkt_do_an
        ]):
            raise ValidationError("Thời gian bắt đầu và kết thúc của đồ án phải bao hàm toàn bộ các khoảng thời gian khác.")

        # Kiểm tra thứ tự thời gian
        timeline = [
            ('tgbd_do_an', 'tgbd_tao_do_an'),
            ('tgbd_tao_do_an', 'tgkt_tao_do_an'),
            ('tgkt_tao_do_an', 'tgbd_dang_ky_de_tai'),
            ('tgbd_dang_ky_de_tai', 'tgkt_dang_ky_de_tai'),
            ('tgkt_dang_ky_de_tai', 'tgbd_lam_do_an'),
            ('tgbd_lam_do_an', 'tgkt_lam_do_an'),
            ('tgkt_lam_do_an', 'tgbd_cham_phan_bien'),
            ('tgbd_cham_phan_bien', 'tgkt_cham_phan_bien'),
            ('tgkt_cham_phan_bien', 'tgbd_cham_hoi_dong'),
            ('tgbd_cham_hoi_dong', 'tgkt_cham_hoi_dong'),
            ('tgkt_cham_hoi_dong', 'tgkt_do_an')
        ]
        
        for start, end in timeline:
            if getattr(input_data, start) >= getattr(input_data, end):
                raise ValidationError(f"Thời gian {start} phải nhỏ  {end}")

    def mutate(self, info, input):
        try:
            # Kiểm tra tính hợp lệ của thời gian
            CreateKeHoachDoAn.validate_time_fields(input)
            
            # Kiểm tra trùng lặp mốc thời gian với kế hoạch đã tồn tại
            existing_plans = KeHoachDoAn.objects.filter(
                tgbd_do_an__lte=input.tgkt_do_an,
                tgkt_do_an__gte=input.tgbd_do_an
            )
            if existing_plans.exists():
                return CreateKeHoachDoAn(
                    ke_hoach_do_an=None,
                    status=False,
                    error=Error(message="Thời gian của kế hoạch mới trùng với kế hoạch đã tồn tại.")
                )
            
            # Tạo kế hoạch đồ án nếu hợp lệ
            ke_hoach_do_an = KeHoachDoAn(
                sl_sinh_vien=input.sl_sinh_vien,
                sl_do_an=input.sl_do_an,
                ky_mo=input.ky_mo,
                tgbd_do_an=input.tgbd_do_an,
                tgkt_do_an=input.tgkt_do_an,
                tgbd_tao_do_an=input.tgbd_tao_do_an,
                tgkt_tao_do_an=input.tgkt_tao_do_an,
                tgbd_dang_ky_de_tai=input.tgbd_dang_ky_de_tai,
                tgkt_dang_ky_de_tai=input.tgkt_dang_ky_de_tai,
                tgbd_lam_do_an=input.tgbd_lam_do_an,
                tgkt_lam_do_an=input.tgkt_lam_do_an,
                tgbd_cham_phan_bien=input.tgbd_cham_phan_bien,
                tgkt_cham_phan_bien=input.tgkt_cham_phan_bien,
                tgbd_cham_hoi_dong=input.tgbd_cham_hoi_dong,
                tgkt_cham_hoi_dong=input.tgkt_cham_hoi_dong,
            )
            ke_hoach_do_an.save()

            return CreateKeHoachDoAn(ke_hoach_do_an=ke_hoach_do_an, status=True, error=None)
        
        except ValidationError as e:
            # Trả về lỗi nếu thời gian không hợp lệ
            return CreateKeHoachDoAn(ke_hoach_do_an=None, status=False, error=Error(message=f"Lỗi xác thực: {str(e)})"))
        except Exception as e:
            # Trả về lỗi nếu có lỗi khác
            return CreateKeHoachDoAn(ke_hoach_do_an=None, status=False, error=f"Lỗi: {str(e)}")
    

# class UpdateKeHoachDoAnInput(graphene.InputObjectType):
#     sl_sinh_vien = graphene.Int()
#     sl_do_an = graphene.Int()
#     ky_mo = graphene.String()
#     tgbd_do_an = graphene.Date()
#     tgkt_do_an = graphene.Date()
#     tgbd_tao_do_an = graphene.Date()
#     tgkt_tao_do_an = graphene.Date()
#     tgbd_dang_ky_de_tai = graphene.Date()
#     tgkt_dang_ky_de_tai = graphene.Date()
#     tgbd_lam_do_an = graphene.Date()
#     tgkt_lam_do_an = graphene.Date()
#     tgbd_cham_phan_bien = graphene.Date()
#     tgkt_cham_phan_bien = graphene.Date()
#     tgbd_cham_hoi_dong = graphene.Date()
#     tgkt_cham_hoi_dong = graphene.Date()


class UpdateKeHoachDoAn(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = KeHoachDoAnInput(required=True)

    status = graphene.Boolean()
    ke_hoach_do_an = graphene.Field(KeHoachDoAnNode)
    error = graphene.Field(Error)

    def validate_time_fields(input):
        """
        Kiểm tra tính hợp lệ của các trường thời gian dựa trên timeline yêu cầu.
        """
        timeline = [
            ('tgbd_do_an', 'tgbd_tao_do_an'),
            ('tgbd_tao_do_an', 'tgkt_tao_do_an'),
            ('tgkt_tao_do_an', 'tgbd_dang_ky_de_tai'),
            ('tgbd_dang_ky_de_tai', 'tgkt_dang_ky_de_tai'),
            ('tgkt_dang_ky_de_tai', 'tgbd_lam_do_an'),
            ('tgbd_lam_do_an', 'tgkt_lam_do_an'),
            ('tgkt_lam_do_an', 'tgbd_cham_phan_bien'),
            ('tgbd_cham_phan_bien', 'tgkt_cham_phan_bien'),
            ('tgkt_cham_phan_bien', 'tgbd_cham_hoi_dong'),
            ('tgbd_cham_hoi_dong', 'tgkt_cham_hoi_dong'),
            ('tgkt_cham_hoi_dong', 'tgkt_do_an')
        ]
        
        for start, end in timeline:
            if getattr(input, start) and getattr(input, end) and getattr(input, start) >= getattr(input, end):
                raise ValidationError(f"{start} phải nhỏ hơn {end}")

    def mutate(self, info, id, input):
        try:
            # Lấy bản ghi kế hoạch đồ án hiện tại
            ke_hoach_do_an = KeHoachDoAn.objects.get(pk=id)
            # Kiểm tra tính hợp lệ của thời gian
            UpdateKeHoachDoAn.validate_time_fields(input)
            
            # Cập nhật các trường nếu có giá trị mới trong `input`
            if input.sl_sinh_vien is not None:
                ke_hoach_do_an.sl_sinh_vien = input.sl_sinh_vien
            if input.sl_do_an is not None:
                ke_hoach_do_an.sl_do_an = input.sl_do_an
            if input.ky_mo is not None:
                ke_hoach_do_an.ky_mo = input.ky_mo
            if input.tgbd_do_an is not None:
                ke_hoach_do_an.tgbd_do_an = input.tgbd_do_an
            if input.tgkt_do_an is not None:
                ke_hoach_do_an.tgkt_do_an = input.tgkt_do_an
            if input.tgbd_tao_do_an is not None:
                ke_hoach_do_an.tgbd_tao_do_an = input.tgbd_tao_do_an
            if input.tgkt_tao_do_an is not None:
                ke_hoach_do_an.tgkt_tao_do_an = input.tgkt_tao_do_an
            if input.tgbd_dang_ky_de_tai is not None:
                ke_hoach_do_an.tgbd_dang_ky_de_tai = input.tgbd_dang_ky_de_tai
            if input.tgkt_dang_ky_de_tai is not None:
                ke_hoach_do_an.tgkt_dang_ky_de_tai = input.tgkt_dang_ky_de_tai
            if input.tgbd_lam_do_an is not None:
                ke_hoach_do_an.tgbd_lam_do_an = input.tgbd_lam_do_an
            if input.tgkt_lam_do_an is not None:
                ke_hoach_do_an.tgkt_lam_do_an = input.tgkt_lam_do_an
            if input.tgbd_cham_phan_bien is not None:
                ke_hoach_do_an.tgbd_cham_phan_bien = input.tgbd_cham_phan_bien
            if input.tgkt_cham_phan_bien is not None:
                ke_hoach_do_an.tgkt_cham_phan_bien = input.tgkt_cham_phan_bien
            if input.tgbd_cham_hoi_dong is not None:
                ke_hoach_do_an.tgbd_cham_hoi_dong = input.tgbd_cham_hoi_dong
            if input.tgkt_cham_hoi_dong is not None:
                ke_hoach_do_an.tgkt_cham_hoi_dong = input.tgkt_cham_hoi_dong

            # Cập nhật quan hệ nếu cần thiết
            
            ke_hoach_do_an.save()
            return UpdateKeHoachDoAn(ke_hoach_do_an=ke_hoach_do_an, status=True, error=Error(message="Update thành công"))
        
        except ValidationError as e:
            # Trả về lỗi nếu thời gian không hợp lệ
            return UpdateKeHoachDoAn(ke_hoach_do_an=None, status=False, error=Error(message=f"Lỗi xác thực: {str(e)})"))
        except KeHoachDoAn.DoesNotExist:
            return UpdateKeHoachDoAn(ke_hoach_do_an=None, status=False, error="Kế hoạch đồ án không tồn tại.")
        except Exception as e:
            return UpdateKeHoachDoAn(ke_hoach_do_an=None, status=False, error="Error exception")
    
class DeleteKeHoachDoAn(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        ke_hoach_do_an = KeHoachDoAn.objects.get(pk=id)
        ke_hoach_do_an.delete()
        return DeleteKeHoachDoAn(success=True)
    
class NotificationInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    status = graphene.Boolean(required=True)
    
class CreateNotification(graphene.Mutation):
    class Arguments:
        input = NotificationInput(required=True)

    status = graphene.Boolean()
    notification = graphene.Field(NotificationNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            notification = Notification.objects.create(
                title=input.title,
                content=input.content,
                status=input.status
            )
            return CreateNotification(status=True, notification=notification)
        except Exception as e:
            error = Error(code="CREATE_ERROR", message=str(e))
            return CreateNotification(status=False, error=error)

class UpdateNotification(graphene.Mutation):    
    class Arguments:
        id = graphene.ID(required=True)
        input = NotificationInput(required=True)
        
    status = graphene.Boolean()
    notification = graphene.Field(NotificationNode)
    error = graphene.Field(Error)
    
    def mutate(self, info, id, input):
        try:
            notification = Notification.objects.get(pk=id)
            if input.title is not None:
                notification.title = input.title
            if input.content is not None:
                notification.content = input.content
            if input.status is not None:
                notification.status = input.status
            notification.save()
            return UpdateNotification(status=True,notification=notification,error=Error(message="Update thành công"))
        except Notification.DoesNotExist:
            error = Error(code="NOT_FOUND", message="Notification not found")
            return UpdateNotification(status=False, error=error)
        except Exception as e:
            error = Error(code="UPDATE_ERROR", message=str(e))
            return UpdateNotification(status=False, error=error)
    
class GradingInput(graphene.InputObjectType):
    detai_id = graphene.ID(required=True)
    diem_huongdan = graphene.Float()
    diem_phanbien = graphene.Float()
    
class CreateGrading(graphene.Mutation):
    class Arguments:
        input = GradingInput(required=True)

    status = graphene.Boolean()
    grading = graphene.Field(GradingNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        # Kiểm tra xem đã có bản ghi nào trùng với detai_id, group_id và user_id chưa
        if Grading.objects.filter(detai_id=input.detai_id).exists():
            error = Error(code="DUPLICATE_RECORD", message="Đề tài nãy đã được chấm điểm.")
            return CreateGrading(status=False, error=error)

        # Nếu không có bản ghi trùng, thực hiện tạo mới
        try:
            grading = Grading.objects.create(
                detai_id=input.detai_id,
                diem_huongdan=input.diem_huongdan,
                diem_phanbien=input.diem_phanbien
            )
            return CreateGrading(status=True, grading=grading, error=Error(message="Tạo thành công"))
        except Exception as e:
            error = Error(code="CREATE_ERROR", message=str(e))
            return CreateGrading(status=False, error=error)

        
class UpdateGradingInput(graphene.InputObjectType):
    diem_huongdan = graphene.Float()
    diem_phanbien = graphene.Float()

class UpdateGrading(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UpdateGradingInput(required=True)

    status = graphene.Boolean()
    grading = graphene.Field(GradingNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            grading = Grading.objects.get(pk=id)
            if input.diem_huongdan is not None:
                grading.diem_huongdan = input.diem_huongdan
            if input.diem_phanbien is not None:
                grading.diem_phanbien = input.diem_phanbien
            grading.save()
            return UpdateGrading(status=True, grading=grading)
        except Grading.DoesNotExist:
            error = Error(code="NOT_FOUND", message="Bản ghi không tồn tại")
            return UpdateGrading(status=False, error=error)
        except Exception as e:
            error = Error(code="UPDATE_ERROR", message=str(e))
            return UpdateGrading(status=False, error=error)

class InviteUserToGroup(graphene.Mutation):
    class Arguments:
        group_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(self, info, group_id, user_id):
        try:
            # Lấy thông tin người dùng từ token
            token = GetToken.getToken(info)
            user = token.user  # Người gửi lời mời (leader của nhóm)

            # Lấy thông tin nhóm
            group_qlda = GroupQLDA.objects.get(pk=group_id)

            # Kiểm tra nếu người dùng đã là thành viên của nhóm
            existing_group = JoinGroup.objects.filter(user__id=user_id, group=group_qlda).first()
            if existing_group:
                return InviteUserToGroup(
                    status=False,
                    error=Error(
                        code="ALREADY_IN_GROUP",
                        message=f"Người dùng {user_id} đã tham gia nhóm {group_qlda.name} trước đó."
                    )
                )

            # Kiểm tra nếu yêu cầu đã tồn tại và chưa được duyệt
            if JoinRequest.objects.filter(user__id=user_id, group=group_qlda, is_approved=False, request_type=RequestType.INVITE.value).exists():
                return InviteUserToGroup(
                    status=False,
                    error=Error(
                        code="REQUEST_ALREADY_SENT",
                        message="Yêu cầu mời tham gia đã được gửi trước đó và đang chờ xử lý."
                    )
                )

            # Kiểm tra số lượng lời mời đã gửi trong nhóm
            invite_count = JoinRequest.objects.filter(user__id=user.id, group=group_qlda, request_type=RequestType.INVITE.value).count()
            if invite_count >= 5:
                return InviteUserToGroup(
                    status=False,
                    error=Error(
                        code="MAX_INVITES_REACHED",
                        message="Bạn đã gửi tối đa 5 lời mời tham gia nhóm này."
                    )
                )

            # Tạo yêu cầu mời tham gia nhóm với request_type là INVITE
            join_request = JoinRequest.objects.create(user_id=user_id, group=group_qlda, request_type=RequestType.INVITE.value)

            # Gửi thông báo cho người được mời
            user_to_invite = User.objects.get(id=user_id)
            user_to_invite.send_notification(f"Bạn đã nhận được lời mời tham gia nhóm {group_qlda.name}.")

            return InviteUserToGroup(status=True)

        except GroupQLDA.DoesNotExist:
            return InviteUserToGroup(
                status=False,
                error=Error(
                    code="GROUP_NOT_FOUND",
                    message="Nhóm không tồn tại."
                )
            )
        except Exception as e:
            return InviteUserToGroup(
                status=False,
                error=Error(
                    code="INVITE_ERROR",
                    message=str(e)
                )
            )


class AcceptGroupInvitation(graphene.Mutation):
    class Arguments:
        join_request_id = graphene.ID(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(self, info, join_request_id):
        try:
            # Lấy thông tin token của người dùng hiện tại
            token = GetToken.getToken(info)
            user = token.user

            # Lấy yêu cầu tham gia từ join_request_id
            join_request = JoinRequest.objects.select_related('group', 'user').get(pk=join_request_id)

            # Kiểm tra xem người dùng này có phải là người được mời hay không
            if join_request.user != user:
                return AcceptGroupInvitation(
                    status=False,
                    error=Error(
                        code="NOT_INVITED",
                        message="Bạn không phải là người được mời tham gia nhóm này."
                    )
                )

            # Kiểm tra xem yêu cầu đã được duyệt hay chưa
            if join_request.is_approved:
                return AcceptGroupInvitation(
                    status=False,
                    error=Error(
                        code="ALREADY_JOINED",
                        message="Bạn đã tham gia nhóm này trước đó."
                    )
                )

            # Kiểm tra nếu nhóm đã đủ số lượng thành viên tối đa
            group = join_request.group
            if group.member_count >= group.max_member:
                return AcceptGroupInvitation(
                    status=False,
                    error=Error(
                        code="GROUP_FULL",
                        message="Nhóm đã đủ số lượng thành viên."
                    )
                )

            # Chấp nhận lời mời và thêm người dùng vào nhóm với vai trò là thành viên
            JoinGroup.objects.create(user=user, group=group, role="member")

            # Tăng số lượng thành viên trong nhóm
            group.member_count += 1
            group.save()

            # Cập nhật trạng thái yêu cầu tham gia là đã được duyệt
            join_request.is_approved = True
            join_request.save()

            # Gửi thông báo cho người quản lý nhóm (leader) về việc người dùng đã gia nhập nhóm
            leader_record = group.join_groups.filter(role="leader").first()
            if leader_record:
                leader_record.user.send_notification(
                    f"{user.email} đã chấp nhận lời mời và gia nhập nhóm {group.name}."
                )

            return AcceptGroupInvitation(status=True)

        except JoinRequest.DoesNotExist:
            return AcceptGroupInvitation(
                status=False,
                error=Error(
                    code="REQUEST_NOT_FOUND",
                    message="Yêu cầu tham gia không tồn tại."
                )
            )
        except Exception as e:
            return AcceptGroupInvitation(
                status=False,
                error=Error(
                    code="JOIN_ERROR",
                    message=str(e)
                )
            )

class Mutation(graphene.ObjectType):
    shipping_fee_create = ShippingFeeCreate.Field()
    shipping_fee_update = ShippingFeeUpdate.Field()
    shipping_fee_delete = ShippingFeeDelete.Field()
    
    transporter_list_create = TransporterListCreate.Field()
    transporter_list_update = TransporterListUpdate.Field()
    transporter_list_delete = TransporterListDelete.Field()
    
    delivery_responsible_create = DeliveryResponsibleCreate.Field()
    delivery_responsible_update = DeliveryResponsibleUpdate.Field()
    delivery_responsible_delete = DeliveryResponsibleDelete.Field()

    deTai_create = DeTaiCreate.Field()
    deTai_update = DeTaiUpdate.Field()

    group_qlda_create = GroupQLDACreate.Field()
    group_qlda_join = GroupQLDAJoin.Field()
    accept_join_request = AcceptJoinRequest.Field()

    create_ke_hoach_do_an = CreateKeHoachDoAn.Field()
    update_ke_hoach_do_an = UpdateKeHoachDoAn.Field()
    delete_ke_hoach_do_an = DeleteKeHoachDoAn.Field()
    
    create_notification = CreateNotification.Field()
    update_notification = UpdateNotification.Field()
    
    create_grading = CreateGrading.Field()
    update_grading = UpdateGrading.Field()

    invite_user_to_group = InviteUserToGroup.Field()
    accept_group_invitation = AcceptGroupInvitation.Field()

