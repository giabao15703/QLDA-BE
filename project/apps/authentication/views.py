import json

from apps.authentication.serializers import UserSerializer, BuyerSerializer, SupplierSerializer
from apps.users.models import Token, ForgotPasswordToken
from apps.users.serializers import SupplierCategorySerializer

from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.http import QueryDict
from django.utils import timezone

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

User = get_user_model()

class ForgotPassword(APIView):
    """
    Forgot password.
    """

    def post(self, request, format='json'):
        email = request.data.get("email")

        if email is None:
            return Response({'error': 'Please provide email', 'success': False})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if not user:
            return Response({'error': 'Email is not exists', 'success': False})

        token, _ = ForgotPasswordToken.objects.get_or_create(user=user)

        message = f"""Create New Password!
            Your username: {user.username}
            Click here http://157.230.247.176/auth/create-new-password/{token} to create new password.
            If you can not click, please copy and paste this link http://157.230.247.176/auth/create-new-password/{token} to your browser."""

        send_mail("NextPro - Create New Password", message, "NextPro <no-reply@nextpro.io>", [user.email], fail_silently=True)

        return Response({'success': True,})


class CheckForgotPasswordToken(APIView):
    """
    Check forgot password token.
    """

    def post(self, request, format='json'):
        token = request.data.get("token")

        if token is None:
            return Response({'error': 'Please provide token'})

        try:
            instance = ForgotPasswordToken.objects.get(pk=token)
        except ForgotPasswordToken.DoesNotExist:
            instance = None

        if not instance:
            return Response({'error': 'Token is not exists'})

        return Response({'success': True})


class CreateNewPassword(APIView):
    """
    Create new password.
    """

    def post(self, request, format='json'):
        token = request.data.get("token")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if token is None:
            return Response({'error': 'Please provide token', 'success': False})

        if password is None:
            return Response({'error': 'Please provide new password', 'success': False})

        if password != confirm_password:
            return Response({'error': 'Password does not match', 'success': False})

        try:
            instance = ForgotPasswordToken.objects.get(pk=token)
        except ForgotPasswordToken.DoesNotExist:
            instance = None

        if not instance:
            return Response({'error': 'Token is not valid', 'success': False})

        user = User.objects.get(pk=instance.user_id)

        if not user:
            return Response({'error': 'User is not exists', 'success': False})

        user.set_password(password)
        user.save()
        instance.delete()

        return Response({'success': True})


class Login(APIView):
    """
    Login.
    """

    class LoginDataSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField(style={'input_type': 'password'})

    serializer_class = LoginDataSerializer

    def post(self, request, format='json'):

        username = request.data.get("username")
        password = request.data.get("password")

        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'})

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'})

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                'user_id': user.id,
                'user_type': user.user_type,
                'token': token.key,
                'email': user.email,
                'logo': '',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'company_short_name': user.get_profile().company_short_name if not user.isAdmin() else '',
            }
        )


class Logout(APIView):
    """
    Logout.
    """

    class LogoutDataSerializer(serializers.Serializer):
        token = serializers.CharField()

    serializer_class = LogoutDataSerializer

    def post(self, request, format='json'):
        token = request.data.get("token")

        if token is None:
            return Response({'error': 'Please provide token'})

        token = Token.objects.filter(pk=token)

        if not token:
            return Response({'error': 'Invalid Credentials'})

        token.delete()

        return Response({'success': True})


class CreateSupplier(APIView):
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    """
    Creates the supplier.
    """

    def post(self, request, format='json'):

        if (User.objects.filter(user_type=3, email=request.data.get('email', ''))).exists():
            return Response({'error': 'Email already exists', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.filter(user_type=3).count() + 1

        if isinstance(request.data, QueryDict):
            data = {**request.data.dict(), 'user_type': 3, 'username': '90' + str(user_count).zfill(4)}

        else:
            data = {**request.data, 'user_type': 3, 'username': '90' + str(user_count).zfill(4)}

        try:
            userSerializer = UserSerializer(data=data)

            userSerializer.is_valid(raise_exception=True)

            user = userSerializer.save()

            supplierSerializer = SupplierSerializer(data={**data, 'user_id': user.id})

            supplierSerializer.is_valid(raise_exception=True)

            supplier = supplierSerializer.save()

            categories = json.loads(request.data.get('categories', '[]'))

            total_percentage = 0
            for category in categories:
                total_percentage = total_percentage + category.get('percentage', 0)

            if total_percentage > 100:
                return Response({'error': 'Total percentage of all categories chosen cannot be greater than 100%', 'success': False})

            for category in categories:
                supplierCategory = SupplierCategorySerializer(data={**category, 'user_supplier_id': supplier.id})
                supplierCategory.is_valid(raise_exception=True)
                supplierCategory.save()

            if user and supplier:

                message = f"""
                <p><img src="{request.build_absolute_uri('/')[:-1]}/static/logo_mail.png" alt="" width="189" height="30" /></p>
                <hr>
                <p>Dear </span><span style="color:red"> {user.last_name} {user.first_name}</span></p>
                <br>
                <p>This email contains your personal access data for the NextPro trading platform.&nbsp;</p>
                <p style="text-align: left;"><strong>Your Login ID:</strong><span style="color:red">{user.username}</span></p>
                <p style="text-align: left;"><strong>Your temporary password:</strong> <span style="color:red">{request.data.get('password')}</span></p>
                <p>Please note that using the copy/paste method of the access information may result in errors if done incorrectly. We always recommend that you enter your access information manually.&nbsp;</span></p>
                <p>For data and privacy purposes, you must change the temporary password provided by us during your first Login attempt. To do so, please follow the instructions given to you by the system.&nbsp;</span></p>
                <p>To access the NextPro Auction Platform, please use the following link: </span><a href ="https://auction.nextpro.io/auth/login">login now</a></p>
                <br>
                <p>Many Thanks and Best Regards,</p>
                <p>Customer Service</p>
                <br>
                <p><strong>NextPro International Procurement Service Company Limited</strong></p>
                <p>10th Floor, Miss Ao Dai Tower</p>
                <p>21 Nguyen Trung Ngan st.,</p>
                <p>Ben Nghe Ward, District 1,</p>
                <p>Ho Chi Minh City, Vietnam</p>
                <p><a href="info@nextpro.io">info@nextpro.io</a> | </span><a href="http://www.nextpro.io">www.nextpro.io</a></p>
                <br>
                <hr>
                <p><span style="color:gray">The information contained in this e-mail is intended only for its addressee and may contain confidential and/or privileged information. If you are not the intended recipient, you are hereby notified that reading, saving, distribution or use of the content of this e-mail is prohibited. If you have received this e-mail in error, please notify the sender and delete the e-mail.</span></p>"""
                try:
                    send_mail(
                        "NextPro - Activate Account", message, "NextPro <no-reply@nextpro.io>", [user.email], html_message=message, fail_silently=True
                    )
                except:
                    print("Fail mail")

                return Response({'success': True,})

        except serializers.ValidationError as error:
            transaction.set_rollback(True)

            return Response({'error': error.detail, 'success': False}, status=error.status_code)

        except BaseException as error:
            transaction.set_rollback(True)
            print(error)
            return Response({'error': 'Server Error', 'success': False}, status=status.HTTP_400_BAD_REQUEST)


class CreateBuyer(APIView):
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    """
    Creates the buyer.
    """

    def post(self, request, format='json'):

        if (User.objects.filter(user_type=2, email=request.data.get('email', ''))).exists():
            return Response({'error': 'Email already exists', 'success': False}, status=status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.filter(user_type=2).count() + 1
        if isinstance(request.data, QueryDict):
            data = {**request.data.dict(), 'user_type': 2, 'username': '80' + str(user_count).zfill(4)}
        else:
            data = {**request.data.dict(), 'user_type': 2, 'username': '80' + str(user_count).zfill(4)}
        try:
            userSerializer = UserSerializer(data=data)
            userSerializer.is_valid(raise_exception=True)

            user = userSerializer.save()

            buyerSerializer = BuyerSerializer(data={**data, 'user_id': user.id})

            buyerSerializer.is_valid(raise_exception=True)

            buyer = buyerSerializer.save()

            if user and buyer:

                message = f"""
                    <p><span style="font-weight: 400;">
                    <img src="{request.build_absolute_uri('/')[:-1]}/static/logo_mail.png" alt="" width="189" height="30" /></span></p>
                    <hr />
                    <p><span style="font-weight: 400;">Dear Mr./Mrs.  </span><span style="font-weight: 400; color: #ff0000;"> {user.last_name} {user.first_name}</span><span style="font-weight: 400;">,</span></p><br>
                    <p><span style="font-weight: 400;">This email contains your personal access data for the NextPro Auction Platform</span></p>
                    <p style="text-align: left; padding-left: 180px;"><strong>Your Login ID:</strong> <span style="font-weight: 400; color: #ff0000;">{user.username}</span></p>
                    <p style="text-align: left; padding-left: 180px;"><strong>Your temporary password:</strong> <span style="font-weight: 400; color: #ff0000;">{request.data.get('password')}</span></p>
                    <p><span style="font-weight: 400;">Please note that using the copy/paste method of the access information may result in errors if done incorrectly. We always recommend that you enter your access information manually.</span></p>
                    <p><span style="font-weight: 400;">For data and privacy purposes, you must change the temporary password provided by us during your first Login attempt. To do so, please follow the instructions given to you by the system</span></p>
                    <p><span style="font-weight: 400;">To access the NextPro Auction Platform, please use the following link: </span><a style="font-weight: 400;" href="https://auction.nextpro.io/auth/login">login now</a></p><br>
                    <p><span style="font-weight: 400;">Many Thanks and Best Regards,</span></p>
                    <p><span style="font-weight: 400;">Customer Service</span></p><br>
                    <p><strong>NextPro International Procurement Service Company Limited</strong></p>
                    <p><span style="font-weight: 400;">10th Floor, Miss Ao Dai Tower</span></p>
                    <p><span style="font-weight: 400;">21 Nguyen Trung Ngan st.,</span></p>
                    <p><span style="font-weight: 400;">Ben Nghe Ward, District 1,</span></p>
                    <p><span style="font-weight: 400;">Ho Chi Minh City, Vietnam</span></p>
                    <p><span style="font-weight: 400; color: #0000ff;">info@nextpro.io</span><a style="font-weight: 400;" href="http://info@nextpro.io"> | </a><a href="http://www.nextpro.io"><span style="font-weight: 400;">www.nextpro.io</span></a></p>
                    <hr />
                    <p><span style="font-weight: 400; color: gray;">The information contained in this e-mail is intended only for its addressee and may contain confidential and/or privileged information. If you are not the intended recipient, you are hereby notified that reading, saving, distribution or use of the content of this e-mail is prohibited. If you have received this e-mail in error, please notify the sender and delete the e-mail.</span></p>
            """
                try:
                    send_mail(
                        "NextPro - Activate Account", message, "NextPro <no-reply@nextpro.io>", [user.email], html_message=message, fail_silently=True
                    )
                except:
                    print("fail mail")
                return Response({'success': True,})

        except serializers.ValidationError as error:
            transaction.set_rollback(True)

            return Response({'error': error.detail, 'success': False}, status=error.status_code)

        except BaseException as error:
            transaction.set_rollback(True)
            print(error)

            return Response({'error': 'Server Error', 'success': False}, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccount(APIView):
    """
    Activate Account.
    """

    def post(self, request, format='json'):
        token = request.data.get("token")

        if token is None:
            return Response({'error': 'Please provide token', 'success': False})

        try:
            user = User.objects.get(activate_token=token)
        except User.DoesNotExist:
            user = None

        if not user:
            return Response({'error': 'Token is not exists', 'success': False})

        if user.activate_time:
            return Response({'error': 'User have already activated', 'success': False})

        user.activate_time = timezone.now()
        user.save()

        return Response({'success': True})

