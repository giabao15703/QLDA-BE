import json

from apps.master_data.models import EmailTemplates, Language
from apps.schema import schema
from apps.users.models import User, Token, ForgotPasswordToken

from graphene_django.utils.testing import GraphQLTestCase

class LoginSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    QUERY = '''
        mutation login($input: LoginInput!) {
            login(user: $input) {
                status
                error{
                    code
                    message
                }
            }
        }
        '''

    @classmethod
    def setUp(self):
        self.language = Language.objects.update_or_create(id=1, name="English1111", item_code="en")
        self.user = User.objects.create_user(username='username_test', password='123123', user_type=1)
        self.token = "Token"
        self.language_code = self.user.language.item_code

    def test_login_mutation_successful(self):
        response = self.query(
            self.QUERY,
            op_name='login',
            input_data={'username': 'username_test', 'password': '123123'},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": self.token},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['login']['status'])

    def test_login_incorrect(self):
        response = self.query(
            self.QUERY,
            op_name='login',
            input_data={'username': 'username_test1', 'password': '1231231'},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": self.token},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['login']['error'].get('code'), "AUTH_01")

    def test_login_invalid(self):
        response = self.query(
            self.QUERY,
            op_name='login',
            input_data={'username': None, 'password': '123123'},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": self.token},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['login']['error'].get('code'), "AUTH_02")

    def test_login_user_disabled(self):
        self.user.status = 2
        self.user.save()
        response = self.query(
            self.QUERY,
            op_name='login',
            input_data={'username': "username_test", 'password': '123123'},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": self.token},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['login']['error'].get('code'), "AUTH_03")


class LogoutSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    QUERY = ''' mutation logout($input:String!){
        logout(token:$input){
            status
            error{
                code
                message
            }
        }
    }
    '''

    @classmethod
    def setUp(self):
        self.language = Language.objects.update_or_create(id=1, name="English", item_code="en")
        self.user = User.objects.create_user(username='username_test', password='123123', user_type=1)
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.language_code = self.user.language.item_code

    def test_logout_mutation_successful(self):
        response = self.query(
            self.QUERY,
            op_name='logout',
            input_data=self.token.key,
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": self.token},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['logout']['status'])

    def test_logout_invalid_credentials(self):
        response = self.query(
            self.QUERY,
            op_name='logout',
            input_data="dfbdhbsadfcnbasikfbhiasfbihasbf",
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": self.token},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['logout']['error'].get('code'), "AUTH_05")

    def test_logout_invalid(self):
        response = self.query(
            self.QUERY, op_name='logout', input_data=None, headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": self.token},
        )
        res = json.loads(response.content)
        self.assertResponseHasErrors(response)


class ForgotPasswordSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    QUERY = ''' mutation forgotPassword($email :String!, $username:String! ){
        forgotPassword(email:$email,  username:$username){
            status
            error{
            code
            message
            }
        }
        }
    '''

    @classmethod
    def setUp(self):
        self.language = Language.objects.update_or_create(id=1, name="English", item_code="en")
        self.user = User.objects.create_user(username='username_test', password='123123', email="test@nng.bz", full_name="test", user_type=1)
        self.language_code = self.user.language.item_code
        self.email_template = EmailTemplates.objects.create(
            item_code="ForgotPassword",
            title="title test",
            content="image:{{image}}--- name: {{name}}--- token :{{Token}}",
            variables="image, name, Token",
        )

    def test_forgot_password_mutation_successful(self):
        response = self.query(
            self.QUERY,
            op_name='forgotPassword',
            variables={"email": "test@nng.bz", "username": "username_test"},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['forgotPassword']['status'])

    def test_forgot_password_invalid(self):
        response = self.query(
            self.QUERY, op_name='forgotPassword', variables={"email": None, "username": None}, headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertResponseHasErrors(response)

    def test_forgot_password_check_user(self):
        response = self.query(
            self.QUERY,
            op_name='forgotPassword',
            variables={"email": "test@nng.bz1", "username": "username_test1"},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['forgotPassword']['error'].get('code'), "AUTH_08")


class CheckForgotPasswordTokenSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    QUERY = '''mutation checkForgotPasswordToken($input :String!){
                checkForgotPasswordToken(token:$input){
                status
                error{
                    code
                    message
                    }
            }
        }
    '''

    @classmethod
    def setUp(self):
        self.language = Language.objects.update_or_create(id=1, name="English", item_code="en")
        self.user = User.objects.create_user(username='username_test', password='123123', user_type=1)
        self.token, _ = ForgotPasswordToken.objects.get_or_create(user=self.user)
        self.language_code = self.user.language.item_code

    def test_check_forgot_passwork_token_successful(self):
        response = self.query(
            self.QUERY, op_name='checkForgotPasswordToken', input_data=self.token.key, headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['checkForgotPasswordToken']['status'])

    def test_check_forgot_passwork_token_not_exists(self):
        response = self.query(
            self.QUERY,
            op_name='checkForgotPasswordToken',
            input_data="dsgfyudsgbhvsdbhidjsbghjisdgihb",
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['checkForgotPasswordToken']['error'].get('code'), "AUTH_09")

    def test_check_forgot_passwork_token_invalid_token(self):
        response = self.query(self.QUERY, op_name='checkForgotPasswordToken', input_data=None, headers={"HTTP_LANGUAGE_CODE": self.language_code},)
        res = json.loads(response.content)

        self.assertResponseHasErrors(response)


class CreateNewPasswordSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    QUERY = '''mutation createNewPassword($confirmPassword:String!,$password:String!,$token: String!){
            createNewPassword(confirmPassword: $confirmPassword,password:$password, token:$token){
            status
            error{
                code
                message
            }
        }
        }
    '''

    @classmethod
    def setUp(self):
        self.language = Language.objects.update_or_create(id=1, name="English", item_code="en")
        self.user = User.objects.create_user(username='username_test', password='123123', user_type=1)
        self.token, _ = ForgotPasswordToken.objects.get_or_create(user=self.user)
        self.language_code = self.user.language.item_code

    def test_create_new_password_successful(self):
        response = self.query(
            self.QUERY,
            op_name='createNewPassword',
            variables={"confirmPassword": "123456789", "password": "123456789", "token": self.token.key},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['createNewPassword']['status'])

    def test_create_new_password_invalid_input(self):
        response = self.query(
            self.QUERY,
            op_name='createNewPassword',
            variables={"confirmPassword": None, "password": None, "token": None},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)

        self.assertResponseHasErrors(response)

    def test_create_new_password_least_6_characters(self):
        response = self.query(
            self.QUERY,
            op_name='createNewPassword',
            variables={"confirmPassword": "123456789", "password": "12345", "token": self.token.key},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['createNewPassword']['error'].get('code'), "AUTH_11")

    def test_create_new_password_not_match(self):
        response = self.query(
            self.QUERY,
            op_name='createNewPassword',
            variables={"confirmPassword": "123456789", "password": "1234145455", "token": self.token.key},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['createNewPassword']['error'].get('code'), "AUTH_12")

    def test_create_new_password_check_token(self):
        response = self.query(
            self.QUERY,
            op_name='createNewPassword',
            variables={"confirmPassword": "123456789", "password": "123456789", "token": "self.token.key"},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['createNewPassword']['error'].get('code'), "AUTH_13")


class ChangePasswordSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    QUERY = '''mutation changePassword($confirmPassword:String!,$newPassword:String!,$password:String!){
        changePassword(confirmPassword:$confirmPassword,newPassword:$newPassword,password:$password){
            status
            error{
            code
            message
            }
        }
        }
    '''

    @classmethod
    def setUp(self):
        self.language = Language.objects.update_or_create(id=1, name="English", item_code="en")
        self.user = User.objects.create_user(username='username_test', password='123123', user_type=1)
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.language_code = self.user.language.item_code

    def test_change_password_successful(self):
        response = self.query(
            self.QUERY,
            op_name='changePassword',
            variables={"newPassword": "123456789", "confirmPassword": "123456789", "password": "123123"},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": "Token " + self.token.key},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['changePassword']['status'])

    def test_change_password_not_match(self):
        response = self.query(
            self.QUERY,
            op_name='changePassword',
            variables={"newPassword": "123456789AA", "confirmPassword": "123456789", "password": "123123"},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": "Token " + self.token.key},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['changePassword']['error'].get('code'), "AUTH_15")

    def test_change_password_invalid_token(self):
        response = self.query(
            self.QUERY,
            op_name='changePassword',
            variables={"newPassword": "123456789", "confirmPassword": "123456789", "password": "123123"},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": "Token " + "self.token.key"},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['changePassword']['error'].get('code'), "AUTH_16")

    def test_change_password_old_password_incorrect(self):
        response = self.query(
            self.QUERY,
            op_name='changePassword',
            variables={"newPassword": "123456789", "confirmPassword": "123456789", "password": "111111"},
            headers={"HTTP_LANGUAGE_CODE": self.language_code, "HTTP_AUTHORIZATION": "Token " + self.token.key},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['changePassword']['error'].get('code'), "AUTH_17")


class InviteRegisterSchemaTest(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    QUERY = '''mutation  inviteRegister($email:String!,$fullName:String!,$userType:Int!){
            inviteRegister(email:$email,fullName:$fullName, userType:$userType){
                status
                error{
                code
                message
                }
            }
        }
    '''

    @classmethod
    def setUp(self):
        self.language = Language.objects.update_or_create(id=1, name="English", item_code="en")
        self.user = User.objects.create_user(username='username_test', password='123123', email="test@nng.bz", user_type=1)
        self.language_code = self.user.language.item_code
        self.email_template_buyer = EmailTemplates.objects.create(
            item_code="InviteBuyerRegister",
            title="title test buyer",
            content="image:{{image}}--- name: {{name}}--- link :{{link}}",
            variables=" image, name,link",
        )
        self.email_template_supplier = EmailTemplates.objects.create(
            item_code="InviteSupplierRegister",
            title="title test supplier",
            content="image:{{image}}--- name: {{name}}--- link :{{link}}",
            variables=" image, name,link",
        )

    def test_invite_register_successful_buyer(self):
        self.user.user_type = 2
        self.user.save()
        response = self.query(
            self.QUERY,
            op_name='inviteRegister',
            variables={"email": "buyer@nng.bz", "fullName": "buyer test", "userType": 2},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['inviteRegister']['status'])

    def test_invite_register_successful_supplier(self):
        self.user.user_type = 3
        self.user.save()
        response = self.query(
            self.QUERY,
            op_name='inviteRegister',
            variables={"email": "supplier@nng.bz", "fullName": "supplier test", "userType": 3},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertTrue(res['data']['inviteRegister']['status'])

    def test_invite_register_email_already_exists_buyer(self):
        self.user.user_type = 2
        self.user.save()
        response = self.query(
            self.QUERY,
            op_name='inviteRegister',
            variables={"email": "test@nng.bz", "fullName": "buyer test", "userType": 2},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['inviteRegister']['error'].get('code'), "AUTH_19")

    def test_invite_register_email_already_exists_supplier(self):
        self.user.user_type = 3
        self.user.save()
        response = self.query(
            self.QUERY,
            op_name='inviteRegister',
            variables={"email": "test@nng.bz", "fullName": "supplier test", "userType": 3},
            headers={"HTTP_LANGUAGE_CODE": self.language_code},
        )
        res = json.loads(response.content)
        self.assertEqual(res['data']['inviteRegister']['error'].get('code'), "AUTH_19")
