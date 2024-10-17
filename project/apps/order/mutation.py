import graphene
from graphene_django import DjangoObjectType
from apps.order.models import (
    Order, 
    OrderAddresses, 
    OrderDeliveryShippingFee, 
    OrderType,
    OrderItems,
    OrderStatus
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
from apps.order.schema import OrderNode
from apps.users.schema import GetToken
from apps.core import Error    
from apps.users.error_code import UserError
from django.db import transaction
from apps.order.error_code import (
    OrderError,
)
from django.core.mail import send_mail
from apps.order.models import Login
from apps.order.schema import LoginNode
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout as django_logout

OrderTypeEnum = graphene.Enum.from_enum(OrderType)

class LoginRoleEnum(graphene.Enum):
    STUDENT = 'student'
    LECTURER = 'lecturer'
    ADMIN_OFFICER = 'admin_officer'
    DEAN = 'dean'


class OrderInput(graphene.InputObjectType):
    buyerId = graphene.Int(required=True) 
    order_type = graphene.String(required=True) 

class OrderUpdateInput(graphene.InputObjectType):
    buyerId = graphene.Int()
    order_status = graphene.String()
    order_type = graphene.String()
    amount = graphene.Float()

class UserLoginInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)
    role = graphene.Field(LoginRoleEnum, required=True)
    emailLogin= graphene.String(required=True)
    is_active = graphene.Boolean(default_value=True)

class LoginRoleInput(graphene.InputObjectType):
    id = graphene.ID(required=True) 
    role = graphene.Field(LoginRoleEnum, required=True)

class LoginStatusInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    is_active = graphene.Boolean(required=True)


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

from django.contrib.auth import authenticate, login as django_login

class LoginMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    status = graphene.Boolean()
    login = graphene.Field(LoginNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, username, password):
        try:
            request = info.context
            login_user = Login.objects.get(username=username)
            if login_user.check_password(password):
                if not login_user.is_active:
                    return LoginMutation(status=False, error=Error(code="AUTH_03", message="Tài khoản đã bị vô hiệu hóa."))
                # Đăng nhập người dùng và tạo session
                django_login(request, login_user)
                return LoginMutation(status=True, login=login_user)
            else:
                return LoginMutation(status=False, error=Error(code="AUTH_01", message="Thông tin đăng nhập không hợp lệ"))
        except Login.DoesNotExist:
            return LoginMutation(status=False, error=Error(code="AUTH_01", message="Thông tin đăng nhập không hợp lệ"))

class LogoutMutation(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info):
        request = info.context
        django_logout(request)
        return LogoutMutation(status=True)


class CreateLoginMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UserLoginInput(required=True)

    status = graphene.Boolean(default_value=False)
    login = graphene.Field(LoginNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, input):
        try:
            # Tạo người dùng mà chưa đặt mật khẩu
            login = Login.objects.create(
                username=input.username,
                emailLogin=input.emailLogin,
                role=input.role,
                is_active=input.is_active
            )
            # Đặt mật khẩu đã băm
            login.set_password(input.password)
            
            # Gửi email thông báo tới người dùng
            send_mail(
                'Thông tin tài khoản của bạn',
                f'Tài khoản của bạn đã được tạo. Username: {input.username}, Password: {input.password}',
                'your-email@gmail.com',
                [input.emailLogin],
                fail_silently=False,
            )

            return CreateLoginMutation(status=True, login=login)
        except Exception as error:
            transaction.set_rollback(True)
            return CreateLoginMutation(status=False, error=Error(code="CREATE_LOGIN_ERROR", message=str(error)))
# Mutation cập nhật thông tin login
class UpdateLoginMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UserLoginInput()

    status = graphene.Boolean(default_value=False)
    login = graphene.Field(LoginNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, id, input):
        try:
            login = Login.objects.get(id=id)
            if input.username:
                login.username = input.username
            if input.password:
                login.set_password(input.password)
            if input.role:
                login.role = input.role
            if input.is_active is not None:
                login.is_active = input.is_active
            login.save()

            return UpdateLoginMutation(status=True, login=login)
        except Exception as error:
            transaction.set_rollback(True)
            return UpdateLoginMutation(status=False, error=Error(code="UPDATE_LOGIN_ERROR", message=str(error)))


# Mutation thay đổi role của login
class UpdateLoginRoleMutation(graphene.Mutation):
    class Arguments:
        input = LoginRoleInput(required=True)

    status = graphene.Boolean(default_value=False)
    login = graphene.Field(LoginNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, input):
        try:
            login = login.objects.get(id=input.id)
            login.role = input.role
            login.save()

            return UpdateLoginRoleMutation(status=True, login=login)
        except Exception as error:
            transaction.set_rollback(True)
            return UpdateLoginRoleMutation(status=False, error=Error(code="UPDATE_ROLE_ERROR", message=str(error)))


# Mutation thay đổi trạng thái của login
class UpdateLoginStatusMutation(graphene.Mutation):
    class Arguments:
        input = LoginStatusInput(required=True)

    status = graphene.Boolean(default_value=False)
    login = graphene.Field(LoginNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, input):
        try:
            login = login.objects.get(id=input.id)
            login.is_active = input.is_active
            login.save()

            return UpdateLoginStatusMutation(status=True, login=login)
        except Exception as error:
            transaction.set_rollback(True)
            return UpdateLoginStatusMutation(status=False, error=Error(code="UPDATE_STATUS_ERROR", message=str(error)))


# Mutation đặt lại mật khẩu, mật khẩu = username
class ResetPasswordMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    status = graphene.Boolean(default_value=False)
    login = graphene.Field(LoginNode)
    error = graphene.Field(Error)

    @staticmethod
    def mutate(root, info, id):
        try:
            login = Login.objects.get(id=id)
            login.set_password(login.username)  # Đặt mật khẩu = username
            login.save()

            return ResetPasswordMutation(status=True, login=login)
        except Exception as error:
            transaction.set_rollback(True)
            return ResetPasswordMutation(status=False, error=Error(code="RESET_PASSWORD_ERROR", message=str(error)))

class Mutation(graphene.ObjectType):
    create_order = OrderCreateMutation.Field()
    update_order = OrderUpdateMutation.Field()
    update_order_status = OrderUpdateStatusMutation.Field()
    delete_order = OrderDeleteMutation.Field()
    create_login = CreateLoginMutation.Field()
    update_login = UpdateLoginMutation.Field()
    update_login_role = UpdateLoginRoleMutation.Field()
    update_login_status = UpdateLoginStatusMutation.Field()
    reset_password = ResetPasswordMutation.Field()
    login= LoginMutation.Field()
    logout = LogoutMutation.Field()

