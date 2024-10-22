import datetime
import filetype
import graphene
import re

from django.db.models import Subquery

from apps.delivery.schema import (
    ShippingFeeNode,
    TransporterListNode,
    DeliveryResponsibleNode,
    GetToken,
    GiangVienNode
)

from apps.delivery.models import (
    ShippingFee,
    TransporterList,
    DeliveryResponsible,
    GiangVien,
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

class GiangVienInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    de_tai = graphene.String(required=True)

class GiangVienCreate(graphene.Mutation):
    class Arguments:
        input = GiangVienInput(required=True)

    status = graphene.Boolean()
    giangVien = graphene.Field(GiangVienNode)
    error = graphene.Field(Error)

    def mutate(root, info, input):
        try:
            giangVien = GiangVien.objects.create(
                name=input.name,
                de_tai=input.de_tai
            )
            return GiangVienCreate(status=True, giangVien=giangVien)
        except Exception as e:
            error = Error(code="CREATE_ERROR", message=str(e))
            return GiangVienCreate(status=False, error=error)
            
class GiangVienUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = GiangVienInput(required=True)

    status = graphene.Boolean()
    giangVien = graphene.Field(lambda: GiangVienNode)
    error = graphene.Field(Error)

    def mutate(root, info, id, input):
        try:
            giangVien = GiangVien.objects.get(pk=id)
            giangVien.name = input.name
            giangVien.de_tai = input.de_tai
            giangVien.save()
            return GiangVienUpdate(status=True, giangVien=giangvien)
        except GiangVien.DoesNotExist:
            error = Error(code="NOT_FOUND", message="GiangVien không tồn tại")
            return GiangVienUpdate(status=False, error=error)
        except Exception as e:
            error = Error(code="UPDATE_ERROR", message=str(e))
            return GiangVienUpdate(status=False, error=error)

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

    giangVien_create = GiangVienCreate.Field()
    giangVien_update = GiangVienUpdate.Field()

