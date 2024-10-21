import graphene
from graphene_django import DjangoObjectType
from apps.order.models import (
    Order, 
    OrderAddresses, 
    OrderDeliveryShippingFee, 
    OrderType,
    OrderItems,
    OrderStatus,
    GiangVien,
    GroupStudent
)   
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from apps.master_data.models import (
    Currency,
)
from apps.users.models import (
    Buyer,
    SupplierProduct,
    SupplierProductFlashSale
)
from apps.order.schema import OrderNode, GiangVienType, GroupStudentType
from apps.users.schema import GetToken
from apps.core import Error    
from apps.users.error_code import UserError
from django.db import transaction
from apps.order.error_code import (
    OrderError,
)
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout as django_logout
from apps.users.models import User
from django.core.exceptions import ValidationError

OrderTypeEnum = graphene.Enum.from_enum(OrderType)

class OrderInput(graphene.InputObjectType):
    buyerId = graphene.Int(required=True) 
    order_type = graphene.String(required=True) 

class GiangVienInput(graphene.InputObjectType):
    name_giang_vien = graphene.String(required=True)
    detai = graphene.String()

class GroupStudentInput(graphene.InputObjectType):
    name_group = graphene.String(required=True)
    giang_vien_id = graphene.ID(required=True)

class OrderUpdateInput(graphene.InputObjectType):
    buyerId = graphene.Int()
    order_status = graphene.String()
    order_type = graphene.String()
    amount = graphene.Float()


#class OrderAddressesInput(DjangoObjectType):
#    class Meta:
#        model = OrderAddresses
#        fields = '__all__'
        
#class OrderShippingFeeInput(graphene.InputObjectType):
#    delivery_shipping_fee = graphene.Float()

# class OrderPaymentDetailsInput(graphene.InputObjectType):
#     payment_method = graphene.Int()
#     payment_status = graphene.Int()
#     amount_paid = graphene.Int()

class OrderItemsInput(graphene.InputObjectType):
    productId = graphene.Int(required=True)
    taxGTGT = graphene.Float()
    amount = graphene.Int(required=True)

class OrderShippingFeeType(DjangoObjectType):
    class Meta:
        model = OrderDeliveryShippingFee
        fields = '__all__'

# class OrderPaymentDetailsType(DjangoObjectType):
#     class Meta:
#         model = OrderPaymentDetails
#         fields = '__all__'

class OrderItemsType(DjangoObjectType):
    class Meta:
        model = OrderItems
        fields = '__all__'

class OrderAddressesCreateInput(graphene.InputObjectType):
    order = graphene.Int()
    address_line1 = graphene.String()
    address_line2 = graphene.String()
    state = graphene.Int()

class OrderCreateMutation(graphene.Mutation):
    class Arguments:
        type = OrderTypeEnum(required=True)
        buyerId = graphene.Int(required=True)
        items = graphene.List(OrderItemsInput, required=True)

    status = graphene.Boolean(default_value=False)
    order = graphene.Field(OrderNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, type, buyerId, items):
        try:
            if not type:
                error = Error(code="CREATE_ORDER_01", message="type is required")
                return OrderCreateMutation(status=False, order=None, error=error)
            if not buyerId:
                error = Error(code="CREATE_ORDER_02", message="buyerId is required")
                return OrderCreateMutation(status=False, order=None, error=error)
            if not items:
                error = Error(code="CREATE_ORDER_03", message="items is required")
                return OrderCreateMutation(status=False, order=None, error=error)

            buyer = Buyer.objects.get(id=buyerId)
            first_product = SupplierProduct.objects.get(id=items[0]['productId'])
            supplier = first_product.user_supplier

            existing_order = Order.objects.filter(buyer=buyer, order_status=OrderStatus.CART.value).first()

            if existing_order:
                if existing_order.supplier != supplier:
                    error = Error(code="CREATE_ORDER_04", message="All items must be from the same supplier")
                    return OrderCreateMutation(status=False, order=None, error=error)

                order = existing_order
                for order_item in items:
                    product = SupplierProduct.objects.get(id=order_item['productId'])

                    if product.user_supplier != supplier:
                        error = Error(code="CREATE_ORDER_05", message="Cannot mix products from different suppliers in one order")
                        return OrderCreateMutation(status=False, order=None, error=error)

                    existing_item = OrderItems.objects.filter(order=order, product=product).first()

                    if existing_item:
                        existing_item.amount += order_item['amount']
                        existing_item.save()
                    else:
                        OrderItems.objects.create(
                            order=order,
                            product=product,
                            amount=order_item['amount']
                        )
            else:
                order = Order.objects.create(
                    buyer=buyer,
                    order_type=type,
                    order_status=OrderStatus.CART.value,
                    supplier=supplier
                )
                for order_item in items:
                    product = SupplierProduct.objects.get(id=order_item['productId'])
                    if product.user_supplier != supplier:
                        error = Error(code="CREATE_ORDER_05", message="Cannot mix products from different suppliers in one order")
                        return OrderCreateMutation(status=False, order=None, error=error)

                    OrderItems.objects.create(
                        order=order,
                        product=product,
                        amount=order_item['amount']
                    )

            total_price = 0
            for item in order.order_items.all():
                supplier_product = SupplierProductFlashSale.objects.get(id=item.product.id)
                price = supplier_product.discounted_price or supplier_product.initial_price or 0
                total_price += price * item.amount



            order.totalAmount = total_price
            order.save()

            return OrderCreateMutation(status=True, order=order)

        except Exception as error:
            transaction.set_rollback(True)
            return OrderCreateMutation(status=False, order=None, error=error)


class OrderUpdateStatusMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        order_status = graphene.String(required=True)

    status = graphene.Boolean()
    order = graphene.Field(OrderNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, id, order_status):
        try:
            try:
                user = GetToken.getToken(info)
            except Exception as e:
                error = Error(code="USER_12", message=UserError.USER_12)
                return OrderUpdateStatusMutation(status=False, error=error)

            order = Order.objects.filter(id=id).first()
            if not order:
                error = Error(code="ORDER_01", message=OrderError.ORDER_01)
                return OrderUpdateStatusMutation(status=False, error=error)

            order.order_status = order_status
            order.save()

            return OrderUpdateStatusMutation(status=True, order=order)

        except Exception as e:
            transaction.set_rollback(True)
            error = Error(code="UPDATE_ORDER_STATUS_FAILED", message=str(e))
            return OrderUpdateStatusMutation(status=False, error=error)
            
class OrderAddressesUpdateInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    order = graphene.Int()
    address_line1 = graphene.String()
    address_line2 = graphene.String()
    country = graphene.Int()
    state = graphene.Int()

class OrderUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True) 
        order = OrderUpdateInput(required=True)  
        order_items = graphene.List(OrderItemsInput)  

    order = graphene.Field(OrderNode)
    error = graphene.Field(Error)
    status = graphene.Boolean()

    @staticmethod
    def mutate(root, info, id, order, order_items):
        try:
            order_instance = Order.objects.get(id=id)

            if order.buyerId:
                buyer = Buyer.objects.get(id=order.buyerId)
                order_instance.buyer = buyer

            if order.order_status:
                order_instance.order_status = order.order_status

            if order.order_type:
                order_instance.order_type = order.order_type

            if order.amount:
                order_instance.amount = order.amount

            order_instance.save()

            if order_items:
                for order_item in order_items:
                    product = SupplierProduct.objects.get(id=order_item['productId'])

                    existing_item = OrderItems.objects.filter(order=order_instance, product=product).first()

                    if existing_item:
                        if order_item['amount'] == 0:
                            existing_item.delete()
                        else:
                            existing_item.amount = order_item['amount']
                            existing_item.save()
                    else:
                        if order_item['amount'] > 0:
                            OrderItems.objects.create(
                                order=order_instance,
                                product=product,
                                amount=order_item['amount']
                            )

            total_price = 0
            for item in order_instance.order_items.all():
                supplier_product = SupplierProductFlashSale.objects.get(id=item.product.id)
                price = supplier_product.discounted_price or supplier_product.initial_price or 0
                total_price += price * item.amount
            order_instance.totalAmount = total_price
            order_instance.save()

            return OrderUpdateMutation(order=order_instance)

        except Order.DoesNotExist:
            error = Error(code="ORDER_NOT_FOUND", message="Đơn hàng không tồn tại.")
            return OrderUpdateMutation(error=error)

        except Exception as e:
            transaction.set_rollback(True)
            error = Error(code="UPDATE_ORDER_FAILED", message=str(e))
            return OrderUpdateMutation(error=error)


class OrderDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info, id):
        try:
            try:
                user = GetToken.getToken(info)
            except:
                error = Error(code="USER_12", message=UserError.USER_12)
                return OrderDeleteMutation(success=False)

            order = Order.objects.get(id=id)
            order.delete()

            return OrderDeleteMutation(success=True)

        except Exception as error:
            transaction.set_rollback(True)
            error = Error(code="ORDER_01", message=str(error))
            return OrderDeleteMutation(success=False)
class CreateGiangVien(graphene.Mutation):
    class Arguments:
        input = GiangVienInput(required=True)

    giang_vien = graphene.Field(lambda: GiangVienType)
    error = graphene.Field(Error)
    status = graphene.Boolean()


    def mutate(self, info, input):
        giang_vien = GiangVien.objects.create(
            name_giang_vien=input.name_giang_vien,
            detai=input.detai
        )
        return CreateGiangVien(giang_vien=giang_vien)

# Mutation tạo nhóm sinh viên và thêm user vào nhóm
class CreateGroupStudent(graphene.Mutation):
    class Arguments:
        input = GroupStudentInput(required=True)
        user_id = graphene.ID(required=True)

    group = graphene.Field(lambda: GroupStudentType)
    error = graphene.Field(Error)
    status = graphene.Boolean()

    def mutate(self, info, input, user_id):
        try:
            user = User.objects.get(id=user_id)
            giang_vien = GiangVien.objects.get(id=input.giang_vien_id)

            # Kiểm tra nếu user đã thuộc nhóm nào khác
            existing_group = GroupStudent.objects.filter(members=user).first()
            if existing_group:
                raise ValidationError("User đã thuộc một nhóm khác.")

            # Tạo nhóm mới và gán user vào
            group = GroupStudent.objects.create(
                name_group=input.name_group,
                giang_vien=giang_vien,
                members=user 
            )

            group.save()
            return CreateGroupStudent(group=group)

        except User.DoesNotExist:
            raise ValidationError("User không tồn tại.")
        except GiangVien.DoesNotExist:
            raise ValidationError("Giảng viên không tồn tại.")
        except Exception as e:
            raise ValidationError(f"Lỗi khi tạo nhóm: {str(e)}")


# Mutation cập nhật nhóm, thêm user mới
class UpdateGroupStudent(graphene.Mutation):
    class Arguments:
        group_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    group = graphene.Field(lambda: GroupStudentType)
    error = graphene.Field(Error)
    status = graphene.Boolean()

    def mutate(self, info, group_id, user_id):
        try:
            group = GroupStudent.objects.get(id=group_id)
            user = User.objects.get(id=user_id)

            # Kiểm tra nếu user đã thuộc nhóm nào
            if user.group_members.exists():
                raise ValidationError("User đã thuộc một nhóm khác.")

            group.members.add(user)
            group.save()

            return UpdateGroupStudent(group=group)

        except GroupStudent.DoesNotExist:
            raise ValidationError("Nhóm không tồn tại.")
        except User.DoesNotExist:
            raise ValidationError("User không tồn tại.")
        except Exception as e:
            raise ValidationError(f"Lỗi khi cập nhật nhóm: {str(e)}")


class Mutation(graphene.ObjectType):
    create_order = OrderCreateMutation.Field()
    update_order = OrderUpdateMutation.Field()
    update_order_status = OrderUpdateStatusMutation.Field()
    delete_order = OrderDeleteMutation.Field()
    create_giang_vien = CreateGiangVien.Field()
    create_group_student = CreateGroupStudent.Field()
    update_group_student = UpdateGroupStudent.Field()
