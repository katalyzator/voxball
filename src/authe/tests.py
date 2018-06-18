from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.utils import timezone
from models import Activation, ResetPasswordRequest, MainUser
from polls.models import Category
from utils import codes, token, password

User = get_user_model()
c = Client()

TEST_USERNAME = u'test@test.ru'
TEST_PASSWORD = u'testpass'
TEST_EMAIL = u'sashachernov4@gmail.com'
TEST_NEW_PASSWORD = u'testpass1'
TEST_PHONE = u'+77086673832'
TEST_KEY = u'ed10e83dde3ebda71ed9f70cae2c3fb5e9c3d34a'
TEST_FB_ACCESS_TOKEN = u'EAACEdEose0cBAGks9NgP8iCoOnLgzqX4vTZAbny3BVuG48PyZCxRG4T4ehgVYZBEYjqx034x7GkwWZB3i8S7UQDTri0IUYmaktxDTuV09p2MIeKVi2mGjV1gQjHjXxU1utOPRJvrfN4k26jEu7hT5qsdmtZBWD5uhtZBdwlKPuWdKhZAqlD3wHrogFTBZCRmkZBUZD'
AUTH_TOKEN_HEADER = "Auth-Token"
STATUS_OK = 200
CODE = "code"


class AuthTestCase(TestCase):

    def common_test(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.json()[CODE], code)

    def common_test_without_json(self, response, status_code):
        self.assertEqual(response.status_code, status_code)

    def get_token(self):
        user = MainUser.objects.create_user(username=TEST_USERNAME,
                                            password=TEST_PASSWORD)

        return token.create_token(user)

    def get_user(self):
        user = MainUser.objects.create_user(username=TEST_USERNAME,
                                            password=TEST_PASSWORD)

        return user

    def get_user_and_token(self):
        user = MainUser.objects.create_user(username=TEST_USERNAME,
                                            password=TEST_PASSWORD)
        return {
            "token": token.create_token(user),
            "user": user
        }

    def test_register_ok(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'email': TEST_USERNAME,
                    'full_name': 'test username',
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_register_ok_without_full_name(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'email': TEST_USERNAME,
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_register_bad_email1(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'email': 'mtemirulansobakagmail.com',
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.BAD_EMAIL)

    def test_register_bad_email2(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'email': 'sashachernov4@gmail',
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.BAD_EMAIL)

    def test_register_bad_email3(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'email': 'mtemirulan@xcom',
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.BAD_EMAIL)

    def test_register_missing_password(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'email': 'mtemirulan@xcom'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.MISSING_REQUIRED_PARAMS)

    def test_register_missing_email(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'full_name': 'Temirulan Mussayev',
                    'password': '123456'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.MISSING_REQUIRED_PARAMS)

    def test_register_wrong_password1(self):
        response = c.post(
                '/api/authe/register/',
                {
                    'email': TEST_EMAIL,
                    'full_name': 'Temirulan Mussayev',
                    'password': '12345'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.PASSWORD_LENGTH_ERROR)

    def test_register_existed_user(self):
        user, _ = User.objects.get_or_create(username=TEST_EMAIL,
                                             email=TEST_EMAIL)
        user.set_password('123456')
        user.is_active = True
        user.save()

        response = c.post(
                '/api/authe/register/',
                {
                    'email': TEST_EMAIL,
                    'full_name': 'Temirulan Mussayev',
                    'password': '123456'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.USERNAME_USED)

    def test_sms_register_ok(self):
        response = c.post(
                '/api/authe/sms_register/',
                {
                    'phone': TEST_PHONE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_sms_register_missing_phone(self):
        response = c.post(
                '/api/authe/sms_register/',
                {
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.MISSING_REQUIRED_PARAMS)

    def test_sms_register_phone_valid(self):
        response = c.post(
                '/api/authe/sms_register/',
                {
                    'phone': '+120012301'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.PHONE_INCORRECT)

    def test_sms_register_phone_used(self):
        user, _ = User.objects.get_or_create(phone=TEST_PHONE)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        response = c.post(
                '/api/authe/sms_register/',
                {
                    'phone': TEST_PHONE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.PHONE_USED)

    def test_sms_resend_ok(self):
        response = c.post(
                '/api/authe/sms_resend/',
                {
                    'phone': TEST_PHONE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_sms_resend_missing_phone(self):
        response = c.post(
                '/api/authe/sms_resend/',
                {
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.MISSING_REQUIRED_PARAMS)

    def test_sms_resend_phone_valid(self):
        response = c.post(
                '/api/authe/sms_resend/',
                {
                    'phone': '+120012301'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.PHONE_INCORRECT)

    def test_sms_user_activate_ok(self):
        Activation.objects.generate(username=TEST_PHONE, code=CODE)

        response = c.post(
                '/api/authe/sms_activate/',
                {
                    'phone': TEST_PHONE,
                    'code': CODE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_sms_user_activate_code_ok(self):
        response = c.post(
                '/api/authe/sms_activate/',
                {
                    'phone': TEST_PHONE,
                    'code': CODE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ACTIVATION_CODE_NOT_FOUND)

    def test_sms_user_activate_time_ok(self):
        Activation.objects.create(username=TEST_PHONE, code=CODE, end_time=timezone.now() - timedelta(minutes=settings.ACTIVATION_TIME), is_active=True)

        response = c.post(
                '/api/authe/sms_activate/',
                {
                    'phone': TEST_PHONE,
                    'code': CODE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ACTIVATION_TIME_EXPIRED)

    def test_login_ok_email(self):
        user, _ = User.objects.get_or_create(email=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        response = c.post(
                '/api/authe/login/',
                {'username': TEST_USERNAME, 'password': TEST_PASSWORD}, HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_login_ok_phone(self):
        user, _ = User.objects.get_or_create(phone=TEST_PHONE)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        response = c.post(
                '/api/authe/login/',
                {'username': TEST_PHONE, 'password': TEST_PASSWORD}, HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_login_missing_username(self):
        response = c.post(
                '/api/authe/login/',
                {
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, 
                         code=codes.MISSING_REQUIRED_PARAMS)

    def test_login_missing_password(self):
        response = c.post(
                '/api/authe/login/',
                {
                    'username': TEST_USERNAME
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.MISSING_REQUIRED_PARAMS)

    def test_login_wrong_username(self):
        response = c.post(
                '/api/authe/login/',
                {
                    'username': TEST_USERNAME,
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.USERNAME_NOT_FOUND)

    def test_login_wrong_password(self):
        user, _ = User.objects.get_or_create(email=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        response = c.post(
                '/api/authe/login/',
                {
                    'username': TEST_USERNAME,
                    'password': 'wrong_password'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INCORRECT_USERNAME_OR_PASSWORD)

    def test_login_not_verified_user(self):
        user, _ = User.objects.get_or_create(email=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.is_active = False
        user.save()

        response = c.post(
                '/api/authe/login/',
                {
                    'username': TEST_USERNAME,
                    'password': TEST_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.USER_NOT_VERIFIED)

    def test_account_activate_ok(self):
        activation, _ = Activation.objects.get_or_create(username=TEST_USERNAME, key=TEST_KEY, end_time=timezone.now() + timedelta(minutes=settings.ACTIVATION_TIME))
        activation.is_active = True
        activation.save()

        user, _ = User.objects.get_or_create(email=TEST_USERNAME)
        user.is_active = True
        user.set_password(TEST_PASSWORD)
        user.save()

        response = c.post('/api/authe/account_activate/{0}/'.format(TEST_KEY))
        self.common_test_without_json(response, status_code=STATUS_OK)

    def test_facebook_login_wrong_token(self):
        response = c.post(
                '/api/authe/facebook_login/',
                {
                    'access_token': TEST_FB_ACCESS_TOKEN+'UJ47'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, 
                         code=codes.FB_OAUTH_TOKEN_INVALID)

    def test_reset_password_ok(self):
        user, _ = User.objects.get_or_create(email=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        response = c.post(
                '/api/authe/reset/',
                {
                    'username': TEST_USERNAME
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_reset_password_missing_email(self):
        response = c.post(
                '/api/authe/reset/',
                {
                    'email': TEST_USERNAME
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, 
                         code=codes.MISSING_REQUIRED_PARAMS)

    def test_reset_password_user_not_found(self):
        response = c.post(
                '/api/authe/reset/',
                {
                    'username': 'slkdflksjdflksjdlkfjslkdfjkl@gmail.com'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.USERNAME_NOT_FOUND)

    def test_change_password_ok(self):
        auth_token = self.get_token()

        response = c.post('/api/authe/change_password/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'current_password': TEST_PASSWORD,
                    'new_password': '123456'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))

        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_change_password_wrong_new_password(self):
        auth_token = self.get_token()

        response = c.post('/api/authe/change_password/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'current_password': TEST_PASSWORD,
                    'new_password': '12345'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))

        self.common_test(response, status_code=STATUS_OK,
                         code=codes.PASSWORD_LENGTH_ERROR)

    def test_change_password_wrong_current_password(self):
        auth_token = self.get_token()

        response = c.post('/api/authe/change_password/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'current_password': 'some_random_password',
                    'new_password': '123456'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))

        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INCORRECT_CURRENT_PASSWORD)

    def test_set_password_by_code_ok(self):
        user, _ = User.objects.get_or_create(username=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        pass_token = str(user.id) + password.generate_password(length=30)
        reset_request, _ = ResetPasswordRequest.objects.get_or_create(user=user, 
                                                                      token=pass_token,
                                                                      deleted=False)
        reset_request.save()

        response = c.post(
                '/api/authe/reset_password/',
                {
                    'token': pass_token,
                    'new_password': TEST_NEW_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_set_password_by_code_not_found(self):
        user = self.get_user()

        pass_token = str(user.id) + password.generate_password(length=30)

        response = c.post(
                '/api/authe/reset_password/',
                {
                    'token': pass_token,
                    'new_password': TEST_NEW_PASSWORD
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.RESET_CODE_NOT_FOUND)

    def test_set_password_by_code_wrong_password(self):
        user = self.get_user()

        pass_token = str(user.id) + password.generate_password(length=30)

        reset_request, _ = ResetPasswordRequest.objects.get_or_create(user=user, token=pass_token, deleted=False)
        reset_request.save()

        response = c.post(
                '/api/authe/reset_password/',
                {
                    'token': pass_token,
                    'new_password': '1'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, 
                         code=codes.PASSWORD_LENGTH_ERROR)

    def test_logout_ok(self):
        auth_token = self.get_token()

        response = c.post('/api/authe/logout/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'token_string': token
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_get_csrf(self):
        auth_token = self.get_token()
        response = c.post('/api/authe/csrf/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'type': "m"
                })
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_verify_csrf(self):
        auth_token = self.get_token()
        response = c.post('/api/authe/csrf/verify/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'csrf_token': token.generate_csrf('m')
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_update_profile_ok(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/update_profile/',
                {   
                    AUTH_TOKEN_HEADER: auth_token,
                    'email': TEST_EMAIL,
                    'full_name': 'Temirulan Mussayev'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))

        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_update_profile_bad_email1(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/update_profile/',
                {   
                    AUTH_TOKEN_HEADER: auth_token,
                    'email': 'mtemirulansobakagmail.com',
                    'full_name': 'Tim'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.BAD_EMAIL)

    def test_update_profile_bad_email2(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/update_profile/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'email': 'sashachernov4@gmail',
                    'full_name': 'Tim'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.BAD_EMAIL)

    def test_update_profile_bad_email3(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/update_profile/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'email': 'mtemirulan@xcom',
                    'full_name': 'Some Awesome Guy'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.BAD_EMAIL)

    def test_update_profile_used_email(self):
        auth_token = self.get_token()

        user, _ = User.objects.get_or_create(email=TEST_EMAIL)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        response = c.post(
                '/api/authe/update_profile/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'email': TEST_EMAIL,
                    'full_name': 'Some Awesome Guy'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.USERNAME_USED)

    def test_update_profile_incorrect_phone(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/update_profile/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'phone': '8708',
                    'full_name': 'Some Awesome Guy'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.PHONE_INCORRECT)

    def test_update_profile_phone_used(self):
        user, _ = User.objects.get_or_create(phone=TEST_PHONE)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()

        user1 = MainUser.objects.create_user(username=TEST_EMAIL,
                                             password=TEST_PASSWORD)
        user_token = token.create_token(user1)

        response = c.post(
                '/api/authe/update_profile/',
                {
                    AUTH_TOKEN_HEADER: user_token,
                    'phone': TEST_PHONE,
                    'full_name': 'Some Awesome Guy'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.PHONE_USED)

    def test_update_profile_categories_match(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/profile/categories/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'category_ids[]': ['1']
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORIES_DOESNT_MATCH)

    def test_get_users(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/get_users/',
                {
                    'tokens[]': [auth_token]
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_update_user_categories_ok(self):
        category, _ = Category.objects.get_or_create(id=1)
        category.is_active = True
        category.save()

        auth_token = self.get_token()

        response = c.post(
                '/api/authe/profile/categories/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'category_ids[]': ['1']
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_update_user_categories_match_ok(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/profile/categories/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'category_ids[]': ['1']
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORIES_DOESNT_MATCH)

    def test_add_delete_category_ok(self):
        category, _ = Category.objects.get_or_create(id=1)
        category.is_active = True
        category.save()

        auth_token = self.get_token()

        response = c.post(
                '/api/authe/profile/category/add_delete/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'category_id': '1'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_add_delete_category_found_ok(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/profile/category/add_delete/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'category_id': '1'
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORY_NOT_FOUND)

    def test_activate_new_phone(self):
        auth_token = self.get_token()
        activation, _ = Activation.objects.get_or_create(code=CODE,
                                                         end_time=timezone.now() + timedelta(minutes=settings.ACTIVATION_TIME),
                                                         username="aidana")
        response = c.post(
                '/api/authe/profile/activate_new_phone/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'code': CODE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK, code=codes.OK)

    def test_activate_new_phone_code_not_found(self):
        auth_token = self.get_token()

        response = c.post(
                '/api/authe/profile/activate_new_phone/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'code': CODE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ACTIVATION_CODE_NOT_FOUND)

    def test_activate_new_phone_time_expired(self):
        auth_token = self.get_token()
        activation, _ = Activation.objects.get_or_create(code=CODE,
                                                         end_time=timezone.now() - timedelta(minutes=settings.ACTIVATION_TIME),
                                                         username="aidana")
        response = c.post(
                '/api/authe/profile/activate_new_phone/',
                {
                    AUTH_TOKEN_HEADER: auth_token,
                    'code': CODE
                },
                HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ACTIVATION_TIME_EXPIRED)
