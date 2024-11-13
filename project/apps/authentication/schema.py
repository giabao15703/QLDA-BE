import graphene
from django.db.models import Subquery

from apps.authentication.error_code import AuthencationError
from apps.users.error_code import UserError
from apps.core import Error
from apps.master_data.models import EmailTemplates, Promotion
from apps.realtime.consumers import ConsumerLoginCheck
from apps.users.models import User, Token, ForgotPasswordToken, Buyer, Supplier
from apps.users.schema import UserNode, AdminNode
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.template import Template, Context
from django.utils import timezone

from graphql import GraphQLError

User = get_user_model()

class LoginInput(graphene.InputObjectType):
    username = graphene.String()
    password = graphene.String()

from django.core.exceptions import ObjectDoesNotExist

class Login(graphene.Mutation):
    token = graphene.String()
    status = graphene.Boolean()
    user = graphene.Field(UserNode)
    admin = graphene.Field(AdminNode)  # Thêm trường admin
    error = graphene.Field(Error)

    class Arguments:
        user = LoginInput(required=True)

    def mutate(root, info, user=None):
        try:
            error = None
            users_login = ConsumerLoginCheck.users
            username_check = 'username_%s' % user.username

            if user.username is None or user.password is None:
                error = Error(code="AUTH_02", message=AuthencationError.AUTH_02)
                raise GraphQLError("AUTH_02")
                
            user = authenticate(username=user.username, password=user.password)
            if not user:
                error = Error(code="AUTH_01", message=AuthencationError.AUTH_01)
                raise GraphQLError("AUTH_01")

            if username_check in users_login and user.user_type == 2:
                error = Error(code="AUTH_18", message=AuthencationError.AUTH_18)
                raise GraphQLError("User can only login to one device at the same time")

            # Xóa token cũ nếu user_type là 2
            if user.user_type == 2:
                Token.objects.filter(user=user).delete()
                token = Token.objects.create(user=user)
            else:
                token, _ = Token.objects.get_or_create(user=user)

            # Truy xuất thông tin admin của user hiện tại
            admin = None
            if hasattr(user, 'admin'):
                admin = user.admin
                print("Admin found:", admin)  # Log để kiểm tra xem admin có được tìm thấy không
            else:
                print("No admin associated with user")

            return Login(status=True, user=user, admin=admin, token=token)
        
        except Exception as err:
            if error is None:
                error = Error(code="UNKNOWN_ERROR", message=str(err))
            return Login(status=False, error=error)



class Logout(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, token):
        if token is None:
            error = Error(code="AUTH_04", message=AuthencationError.AUTH_04)
            return Logout(status=False, error=error)

        token = Token.objects.filter(pk=token)

        if not token:
            error = Error(code="AUTH_05", message=AuthencationError.AUTH_05)
            return Logout(status=False, error=error)
        token.delete()

        return Logout(status=True)

class ForgotPassword(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, username, email):
        if username is None:
            error = Error(code="AUTH_06", message=AuthencationError.AUTH_06)
            return ForgotPassword(status=False, error=error)

        if email is None:
            error = Error(code="AUTH_07", message=AuthencationError.AUTH_07)
            return ForgotPassword(status=False, error=error)

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            error = Error(code="AUTH_08", message=AuthencationError.AUTH_08)
            return ForgotPassword(status=False, error=error)

        token, _ = ForgotPasswordToken.objects.get_or_create(user=user)

        email = EmailTemplates.objects.get(item_code='ForgotPassword')
        title = email.translated.title
        t = Template(email.translated.content)
        c = Context({"image": info.context.build_absolute_uri("/static/logo_mail.png"), "name": user.full_name, "Token": token.key,})
        output = t.render(c)
        send_mail(title, output, "NextPro <no-reply@nextpro.io>", [user.email], html_message=output, fail_silently=True)
        return ForgotPassword(status=True)

class CheckForgotPasswordToken(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, token):
        if token is None:
            error = Error(code="AUTH_04", message=AuthencationError.AUTH_04)
            return CheckForgotPasswordToken(status=False, error=error)

        try:
            instance = ForgotPasswordToken.objects.get(pk=token)
        except ForgotPasswordToken.DoesNotExist:
            instance = None

        if not instance:
            error = Error(code="AUTH_09", message=AuthencationError.AUTH_09)
            return CheckForgotPasswordToken(status=False, error=error)

        return CheckForgotPasswordToken(status=True)

class CreateNewPassword(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, token, password, confirm_password):
        if token is None:
            error = Error(code="AUTH_04", message=AuthencationError.AUTH_04)
            return CreateNewPassword(status=False, error=error)

        if password is None:
            error = Error(code="AUTH_10", message=AuthencationError.AUTH_10)
            return CreateNewPassword(status=False, error=error)
            raise GraphQLError('AUTH_10')

        if len(password) < 6:
            error = Error(code="AUTH_11", message=AuthencationError.AUTH_11)
            return CreateNewPassword(status=False, error=error)

        if password != confirm_password:
            error = Error(code="AUTH_12", message=AuthencationError.AUTH_12)
            return CreateNewPassword(status=False, error=error)

        try:
            instance = ForgotPasswordToken.objects.get(pk=token)
        except ForgotPasswordToken.DoesNotExist:
            instance = None

        if not instance:
            error = Error(code="AUTH_13", message=AuthencationError.AUTH_13)
            return CreateNewPassword(status=False, error=error)

        user = User.objects.get(pk=instance.user_id)

        if not user:
            error = Error(code="AUTH_14", message=AuthencationError.AUTH_14)
            return CreateNewPassword(status=False, error=error)

        user.set_password(password)
        user.save()
        instance.delete()
        return CreateNewPassword(status=True)

class ChangePassword(graphene.Mutation):
    class Arguments:
        password = graphene.String(required=True)
        new_password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, password, new_password, confirm_password):
        if new_password != confirm_password:
            error = Error(code="AUTH_15", message=AuthencationError.AUTH_15)
            return ChangePassword(status=False, error=error)

        if len(new_password) < 6:
            error = Error(code="AUTH_11", message=AuthencationError.AUTH_11)
            return ChangePassword(status=False, error=error)

        try:
            key = info.context.headers['Authorization'].split(" ")
            key = key[-1]
            token = Token.objects.get(key=key)
        except:
            error = Error(code="AUTH_16", message=AuthencationError.AUTH_16)
            return ChangePassword(status=False, error=error)

        user = authenticate(username=token.user.username, password=password)

        if not user:
            error = Error(code="AUTH_17", message=AuthencationError.AUTH_17)
            return ChangePassword(status=False, error=error)

        user.set_password(new_password)
        user.save()
        return ChangePassword(status=True)

class InviteRegister(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        full_name = graphene.String(required=True)
        user_type = graphene.Int(required=True)
        referral_code = graphene.String(required=False)

    status = graphene.Boolean()
    error = graphene.Field(Error)

    def mutate(root, info, email, full_name, user_type, referral_code=""):
        if user_type == 2:
            if User.objects.filter(user_type=2, email=email).exists():
                error = Error(code="AUTH_19", message=AuthencationError.AUTH_19)
                return InviteRegister(status=False, error=error)
            email_template = EmailTemplates.objects.get(item_code='InviteBuyerRegister')
            link = "https://auction.nextpro.io/auth/register/register-buyer"
        elif user_type == 3:
            if User.objects.filter(user_type=3, email=email).exists():
                error = Error(code="AUTH_19", message=AuthencationError.AUTH_19)
                return InviteRegister(status=False, error=error)
            email_template = EmailTemplates.objects.get(item_code='InviteSupplierRegister')
            link = "https://auction.nextpro.io/auth/register/register-supplier"
        else:
            raise GraphQLError("Invalid user type")
        referral_by = ""
        if len(referral_code) > 0:
            promotions = Promotion.objects.filter(name=referral_code, status=True)
            if promotions.exists():
                promotion = promotions.first()
                referral_by = promotion.user_given
                if email_template.translated.translation is None or email_template.translated.translation.language_code == "en":
                    referral_by = " by " + referral_by + " - Referral code " + referral_code
                elif email_template.translated.translation.language_code == "vi":
                    referral_by += " - Mã giới thiệu " + referral_code
                referral_by+=" "
            else:
                error = Error(code="USER_34", message=UserError.USER_34)
                raise GraphQLError('USER_34')
        message = Template(email_template.translated.content).render(
            Context({"image": info.context.build_absolute_uri("/static/logo_mail.png"), "name": full_name, "link": link, "referralBy": referral_by})
        )
        send_mail(email_template.translated.title, message, "NextPro <no-reply@nextpro.io>", [email], html_message=message, fail_silently=True)
        return InviteRegister(status=True)

class Mutation(graphene.ObjectType):
    login = Login.Field()
    logout = Logout.Field()
    forgot_password = ForgotPassword.Field()
    check_forgot_password_token = CheckForgotPasswordToken.Field()
    create_new_password = CreateNewPassword.Field()
    change_password = ChangePassword.Field()
    invite_register = InviteRegister.Field()
