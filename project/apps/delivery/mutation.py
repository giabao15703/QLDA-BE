import datetime
import filetype
import graphene
import re
import random
from graphene import relay 
from django.db.models import Subquery
from graphene_django import DjangoObjectType
from django.utils import timezone
from django.core.exceptions import ValidationError  # Thêm dòng này để import ValidationError
from apps.delivery.schema import (
    ShippingFeeNode,
    TransporterListNode,
    DeliveryResponsibleNode,
    GetToken,
    DeTaiNode,
    GroupQLDANode,
    KeHoachDoAnNode,

)

from apps.delivery.models import (
    ShippingFee,
    TransporterList,
    DeliveryResponsible,
    DeTai,
    GroupQLDA,
    JoinGroup,
    JoinRequest,
    User,
    KeHoachDoAn
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
    idgvhuongdan = graphene.ID(required=True)  # ID của giảng viên hướng dẫn
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
            giang_vien = User.objects.get(id=input.idgvhuongdan)

            # Lấy kế hoạch đồ án hợp lệ
            now = timezone.now().date()
            ke_hoach_do_an = KeHoachDoAn.objects.filter(
                tgbd_tao_do_an__lte=now,
                tgkt_tao_do_an__gte=now
            ).first()

            if not ke_hoach_do_an:
                error = Error(code="NO_VALID_KEHOACH", message="Không có kế hoạch đồ án nào trong thời gian cho phép tạo đề tài.")
                return DeTaiCreate(status=False, error=error)

            # Tạo đề tài với các thuộc tính được yêu cầu
            de_tai = DeTai.objects.create(
                idgvhuongdan=giang_vien,
                idkehoach=ke_hoach_do_an,
                tendoan=input.tendoan,
                mota=input.mota,
                madoan=DeTai.generate_unique_madoan(),
                chuyennganh=giang_vien.chuyennganh,  # Lấy chuyên ngành từ giảng viên
                trangthai="0"  # Đặt trạng thái mặc định là "0" (chưa duyệt)
            )

            return DeTaiCreate(status=True, de_tai=de_tai)

        except User.DoesNotExist:
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
    trangthai = graphene.String()  # Chỉ trưởng khoa có thể cập nhật
    yeucau = graphene.String()      # Chỉ trưởng khoa có thể cập nhật


class DeTaiUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = DeTaiUpdateInput(required=True)

    status = graphene.Boolean()
    de_tai = graphene.Field(DeTaiNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            # Lấy đối tượng đề tài cần cập nhật
            de_tai = DeTai.objects.get(id=id)
            user = info.context.user

            # Kiểm tra quyền hạn của người dùng
            if user.role == "TruongKhoa":  # Giả sử Trưởng khoa có role là "TruongKhoa"
                # Cho phép trưởng khoa cập nhật trạng thái và yêu cầu
                if input.trangthai is not None:
                    de_tai.trangthai = input.trangthai
                if input.yeucau is not None:
                    de_tai.yeucau = input.yeucau

            elif user.id == de_tai.idgvhuongdan.id:
                # Nếu là giảng viên hướng dẫn, chỉ cho phép cập nhật tên đồ án và mô tả
                if input.tendoan is not None:
                    de_tai.tendoan = input.tendoan
                if input.mota is not None:
                    de_tai.mota = input.mota
            else:
                # Người dùng không có quyền cập nhật
                error = Error(code="PERMISSION_DENIED", message="Bạn không có quyền cập nhật đề tài này.")
                return DeTaiUpdate(status=False, error=error)

            # Lưu thay đổi
            de_tai.save()
            return DeTaiUpdate(status=True, de_tai=de_tai)

        except DeTai.DoesNotExist:
            error = Error(code="NOT_FOUND", message="Đề tài không tồn tại")
            return DeTaiUpdate(status=False, error=error)
        except Exception as e:
            error = Error(code="UPDATE_ERROR", message=str(e))
            return DeTaiUpdate(status=False, error=error)



import graphene
from django.utils import timezone

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
        user_email = graphene.String(required=True)

    status = graphene.Boolean()
    group_qlda = graphene.Field(GroupQLDANode)
    error = graphene.Field(Error)

    def mutate(root, info, input, user_email):
        try:
            # Tìm người dùng dựa trên email
            user_creating_group = User.objects.get(email=user_email)

            # Tạo nhóm mới
            group_qlda = GroupQLDA(
                name=input.name,
            )
            group_qlda.save()

            # Thêm người dùng vào nhóm với vai trò trưởng nhóm
            JoinGroup.objects.create(user=user_creating_group, group=group_qlda, role="leader")

            # Cập nhật số lượng thành viên trong nhóm
            group_qlda.member_count += 1
            group_qlda.save()

            return GroupQLDACreate(status=True, group_qlda=group_qlda)
        except User.DoesNotExist:
            error = Error(code="USER_NOT_FOUND", message="Người dùng không tồn tại")
            return GroupQLDACreate(status=False, error=error)
        except Exception as e:
            error = Error(code="CREATE_ERROR", message=str(e))
            return GroupQLDACreate(status=False, error=error)

class GroupQLDAJoin(graphene.Mutation):
    class Arguments:
        group_id = graphene.ID(required=True)
        user_email = graphene.String(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, group_id, user_email):
        try:
            # Tìm nhóm dựa trên group_id
            group_qlda = GroupQLDA.objects.get(pk=group_id)

            # Tìm người dùng dựa trên email
            user = User.objects.get(email=user_email)

            # Kiểm tra nếu yêu cầu đã tồn tại hoặc người dùng đã ở trong nhóm
            if JoinRequest.objects.filter(user=user, group=group_qlda, is_approved=False).exists():
                return GroupQLDAJoin(status=False, error=Error(code="REQUEST_ALREADY_SENT", message="Yêu cầu đã được gửi"))

            # Tạo yêu cầu tham gia mới
            join_request = JoinRequest.objects.create(user=user, group=group_qlda)

            # Gửi thông báo đến leader của nhóm
            leader = group_qlda.join_groups.filter(role="leader").first().user
            send_notification(
                user=leader,
                message=f"{user.email} đã gửi yêu cầu tham gia vào nhóm {group_qlda.name}"
            )

            return GroupQLDAJoin(status=True)
        except GroupQLDA.DoesNotExist:
            return GroupQLDAJoin(status=False, error=Error(code="GROUP_NOT_FOUND", message="Nhóm không tồn tại"))
        except User.DoesNotExist:
            return GroupQLDAJoin(status=False, error=Error(code="USER_NOT_FOUND", message="Người dùng không tồn tại"))
        except Exception as e:
            return GroupQLDAJoin(status=False, error=Error(code="JOIN_ERROR", message=str(e)))


class AcceptJoinRequest(graphene.Mutation):
    class Arguments:
        join_request_id = graphene.ID(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, join_request_id):
        try:
            # Lấy yêu cầu tham gia dựa trên ID
            join_request = JoinRequest.objects.get(pk=join_request_id)

            # Kiểm tra nếu user hiện tại là leader của nhóm dựa trên leader_user_id
            if info.context.user.id != join_request.leader_user_id:
                return AcceptJoinRequest(
                    status=False,
                    error=Error(code="PERMISSION_DENIED", message="Bạn không có quyền chấp nhận yêu cầu này")
                )

            # Đánh dấu yêu cầu là đã được phê duyệt
            join_request.is_approved = True
            join_request.save()

            # Thêm người dùng vào nhóm với vai trò là thành viên
            JoinGroup.objects.create(user=join_request.user, group=join_request.group, role="member")

            # Tăng số lượng thành viên trong nhóm
            join_request.group.member_count += 1
            join_request.group.save()

            # Gửi thông báo tới leader về việc chấp nhận yêu cầu
            join_request.send_notification(f"User {join_request.user.id} đã được chấp nhận vào nhóm {join_request.group.id}.")

            return AcceptJoinRequest(status=True)
        except JoinRequest.DoesNotExist:
            return AcceptJoinRequest(
                status=False,
                error=Error(code="REQUEST_NOT_FOUND", message="Yêu cầu tham gia không tồn tại")
            )
        except Exception as e:
            return AcceptJoinRequest(
                status=False,
                error=Error(code="ACCEPT_ERROR", message=str(e))
            )

class KeHoachDoAnType(DjangoObjectType):
    class Meta:
        model = KeHoachDoAn
        fields = "__all__"
        interfaces = (relay.Node,)

class CreateKeHoachDoAn(graphene.Mutation):
    class Arguments:
        sl_sinh_vien = graphene.Int(required=True)
        sl_do_an = graphene.Int(required=True)
        ky_mo = graphene.String(required=True)
        tgbd_do_an = graphene.Date(required=True)
        tgkt_do_an = graphene.Date(required=True)
        tgbd_tao_do_an = graphene.Date(required=True)
        tgkt_tao_do_an = graphene.Date(required=True)
        tgbd_dang_ky_de_tai = graphene.Date(required=True)
        tgkt_dang_ky_de_tai = graphene.Date(required=True)
        tgbd_lam_do_an = graphene.Date(required=True)
        tgkt_lam_do_an = graphene.Date(required=True)
        tgbd_cham_phan_bien = graphene.Date(required=True)
        tgkt_cham_phan_bien = graphene.Date(required=True)
        tgbd_cham_hoi_dong = graphene.Date(required=True)
        tgkt_cham_hoi_dong = graphene.Date(required=True)
        user_id = graphene.ID(required=True)

    ke_hoach_do_an = graphene.Field(KeHoachDoAnNode)

    def validate_time_fields(**kwargs):
        """
        Kiểm tra tính hợp lệ của các trường thời gian dựa trên timeline yêu cầu:
        tgbd_do_an <= tgbd_tao_do_an <= tgkt_tao_do_an <= tgbd_dang_ky_de_tai <= tgkt_dang_ky_de_tai <=
        tgbd_lam_do_an <= tgkt_lam_do_an <= tgbd_cham_phan_bien <= tgkt_cham_phan_bien <= 
        tgbd_cham_hoi_dong <= tgkt_cham_hoi_dong <= tgkt_do_an
        """

        tgbd_do_an = kwargs.get('tgbd_do_an')
        tgkt_do_an = kwargs.get('tgkt_do_an')

        if not all([
            tgbd_do_an <= kwargs.get('tgbd_tao_do_an') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgkt_tao_do_an') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgbd_dang_ky_de_tai') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgkt_dang_ky_de_tai') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgbd_lam_do_an') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgkt_lam_do_an') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgbd_cham_phan_bien') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgkt_cham_phan_bien') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgbd_cham_hoi_dong') <= tgkt_do_an,
            tgbd_do_an <= kwargs.get('tgkt_cham_hoi_dong') <= tgkt_do_an
        ]):
            raise ValidationError("Thời gian bắt đầu và kết thúc của đồ án phải bao hàm toàn bộ các khoảng thời gian khác.")

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
            if kwargs.get(start) > kwargs.get(end):
                raise ValidationError(f"{start} phải nhỏ hơn hoặc bằng {end}")

    def mutate(self, info, **kwargs):
        # Kiểm tra user
        user = User.objects.get(pk=kwargs.get('user_id'))
        
        # Kiểm tra tính hợp lệ của thời gian
        CreateKeHoachDoAn.validate_time_fields(**kwargs)
        
        
        # Tạo kế hoạch đồ án nếu hợp lệ
        ke_hoach_do_an = KeHoachDoAn(
            sl_sinh_vien=kwargs.get('sl_sinh_vien'),
            sl_do_an=kwargs.get('sl_do_an'),
            ky_mo=kwargs.get('ky_mo'),
            tgbd_do_an=kwargs.get('tgbd_do_an'),
            tgkt_do_an=kwargs.get('tgkt_do_an'),
            tgbd_tao_do_an=kwargs.get('tgbd_tao_do_an'),
            tgkt_tao_do_an=kwargs.get('tgkt_tao_do_an'),
            tgbd_dang_ky_de_tai=kwargs.get('tgbd_dang_ky_de_tai'),
            tgkt_dang_ky_de_tai=kwargs.get('tgkt_dang_ky_de_tai'),
            tgbd_lam_do_an=kwargs.get('tgbd_lam_do_an'),
            tgkt_lam_do_an=kwargs.get('tgkt_lam_do_an'),
            tgbd_cham_phan_bien=kwargs.get('tgbd_cham_phan_bien'),
            tgkt_cham_phan_bien=kwargs.get('tgkt_cham_phan_bien'),
            tgbd_cham_hoi_dong=kwargs.get('tgbd_cham_hoi_dong'),
            tgkt_cham_hoi_dong=kwargs.get('tgkt_cham_hoi_dong'),
            user=user
        )
        ke_hoach_do_an.save()
        return CreateKeHoachDoAn(ke_hoach_do_an=ke_hoach_do_an)

class UpdateKeHoachDoAn(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        sl_sinh_vien = graphene.Int()
        sl_do_an = graphene.Int()
        ky_mo = graphene.String()
        tgbd_do_an = graphene.Date()
        tgkt_do_an = graphene.Date()
        tgbd_tao_do_an = graphene.Date()
        tgkt_tao_do_an = graphene.Date()
        tgbd_dang_ky_de_tai = graphene.Date()
        tgkt_dang_ky_de_tai = graphene.Date()
        tgbd_lam_do_an = graphene.Date()
        tgkt_lam_do_an = graphene.Date()
        tgbd_cham_phan_bien = graphene.Date()
        tgkt_cham_phan_bien = graphene.Date()
        tgbd_cham_hoi_dong = graphene.Date()
        tgkt_cham_hoi_dong = graphene.Date()
        user_id = graphene.ID()

    ke_hoach_do_an = graphene.Field(KeHoachDoAnNode)

    def validate_time_fields(**kwargs):
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
            if kwargs.get(start) and kwargs.get(end) and kwargs.get(start) > kwargs.get(end):
                raise ValidationError(f"{start} phải nhỏ hơn hoặc bằng {end}")

    def mutate(self, info, id, **kwargs):
        # Lấy bản ghi kế hoạch đồ án hiện tại
        ke_hoach_do_an = KeHoachDoAn.objects.get(pk=id)
        
        # Kiểm tra tính hợp lệ của thời gian
        UpdateKeHoachDoAn.validate_time_fields(**kwargs)
        
        # Cập nhật các trường nếu có giá trị mới trong `kwargs`
        for key, value in kwargs.items():
            if value is not None:
                setattr(ke_hoach_do_an, key, value)

        # Cập nhật quan hệ nếu cần thiết
        if 'user_id' in kwargs:
            ke_hoach_do_an.user = User.objects.get(pk=kwargs.get('user_id'))
        
        ke_hoach_do_an.save()
        return UpdateKeHoachDoAn(ke_hoach_do_an=ke_hoach_do_an)
    
class DeleteKeHoachDoAn(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        ke_hoach_do_an = KeHoachDoAn.objects.get(pk=id)
        ke_hoach_do_an.delete()
        return DeleteKeHoachDoAn(success=True)

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

