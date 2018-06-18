# -*- coding: utf-8 -*-
from authe import tasks
from authe.models import Activation, ResetPasswordRequest
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.files import File
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from statistics.models import UserStat
from utils import codes, messages, token, http, time_utils, oauth, \
    password
from utils.Constants import EMAIL_REGISTER, TELEPHONE_REGISTER, \
    FACEBOOK_REGISTER
import logging
import phonenumbers


logger = logging.getLogger(__name__)
User = get_user_model()


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["email", "password"])
def register(request):
    """
    @api {post} /authe/register/ Registration method
    @apiName register
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} email Email of user.
    @apiParam {String} password Password of user, minimum length: 6.
    @apiParam {String} full_name Full name of user [optional].
    @apiParam {Number} profile_type User's type: {"0": "default user", "1": "partner", "2": "media"}.
    @apiParam {String} partner_details Partner/media details.
    @apiParam {String} partner_author Partner/media author.
    @apiSuccess {Object} result Json representation of user.
    """
    try:
        email = request.POST.get('email', '').lower()
        try:
            validate_email(email)
        except Exception as e:
            return http.code_response(code=codes.BAD_EMAIL,
                                      message=messages.BAD_EMAIL.format(email))
        _password = request.POST.get('password', '')
        if len(_password) < settings.PASSWORD_LENGTH:
            return http.code_response(
                code=codes.PASSWORD_LENGTH_ERROR,
                message=messages.PASSWORD_LENGTH_ERROR.format(len(_password)))
        if User.objects.filter(email__iexact=email, is_active=True).exists():
            return http.code_response(code=codes.USERNAME_USED,
                                      message=messages.USERNAME_USED)

        activation_key = Activation.objects.generate(username=email)
        link = settings.EMAIL_ACTIVATION_URL.format(token=activation_key)
        try:
            tasks.email(to=email,
                              subject=messages.REGISTRATION_COMPLETION,
                              message=render_to_string(
                                  'emails/activate_account.html',
                                  context={'key': activation_key,
                                           'link': link},
                                  request=request))
        except Exception as e:
            logger.error(e)
            return http.code_response(code=codes.EMAIL_SERVICE_ERROR,
                                      message=messages.EMAIL_SERVICE_ERROR)
        try:
            profile_type = int(request.POST.get("profile_type", "0"))
            if profile_type not in [0, 1]:
                profile_type = 0
        except:
            profile_type = 0
        new_user, _ = User.objects.get_or_create(username=email)
        new_user.set_password(_password)
        new_user.profile_type = profile_type
        new_user.full_name = request.POST.get("full_name", "")
        new_user.email = email
        new_user.email_activated = False
        new_user.is_active = False
        new_user.user_type = EMAIL_REGISTER
        new_user.save()
        return {
            'user': new_user.full()
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["phone"])
def sms_register(request):
    """
    @api {post} /authe/sms_register/ Sms Registration method
    @apiName sms_register
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} phone Phone of user.
    @apiParam {Number} age Age of user [optional].
    @apiSuccess {Object} Json with code
    """
    phone = request.POST["phone"].lower()
    # Validation phone number
    try:
        phone_object = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(phone_object):
            return http.code_response(code=codes.PHONE_INCORRECT,
                                      message=messages.PHONE_INCORRECT)
    except:
        return http.code_response(code=codes.PHONE_INCORRECT,
                                  message=messages.PHONE_INCORRECT)

    if User.objects.filter(phone=phone, is_active=True).exists():
        return http.code_response(code=codes.PHONE_USED,
                                  message=messages.PHONE_USED)
    else:
        code = password.generate_sms_code()
        Activation.objects.generate(username=phone, code=code)
        tasks.send_message(phone, settings.SMS_ACTIVATION_TEXT.format(
            password=code))
    return http.ok_response()


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["phone"])
def sms_resend(request):
    """
    @api {post} /authe/sms_resend/ Sms resend method
    @apiName sms_resend
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} phone Phone of user.
    @apiSuccess {Object} Json with code
    """
    try:
        phone = request.POST["phone"].lower()
        # Validation phone number
        try:
            phone_object = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(phone_object):
                return http.code_response(code=codes.PHONE_INCORRECT,
                                          message=messages.PHONE_INCORRECT)
        except:
            return http.code_response(code=codes.PHONE_INCORRECT,
                                      message=messages.PHONE_INCORRECT)
        code = password.generate_sms_code()
        Activation.objects.generate(username=phone, code=code)
        tasks.send_message(
            phone, settings.SMS_ACTIVATION_TEXT.format(password=code))
        return http.ok_response()
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["phone", "code"])
def sms_user_activate(request):
    """
    @api {post} /authe/sms_activate/ Sms activation method
    @apiName sms_user_activate
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} phone Phone of user.
    @apiParam {Number} code Code sent to user.
    @apiSuccess {Object} Json with code
    """
    phone = request.POST["phone"]
    code = request.POST["code"]
    now = timezone.now()
    try:
        activation = Activation.objects.get(code=code, username=phone,
                                            is_active=True)
    except:
        return http.code_response(code=codes.ACTIVATION_CODE_NOT_FOUND,
                                  message=messages.ACTIVATION_CODE_NOT_FOUND)
    if activation.end_time < now:
        return http.code_response(code=codes.ACTIVATION_TIME_EXPIRED,
                                  message=messages.ACTIVATION_TIME_EXPIRED)
    activation.is_active = False
    activation.save()
    user, _ = User.objects.get_or_create(username=phone)
    user.is_active = True
    user.phone = phone
    user.set_password(activation.code)
    user.user_type = TELEPHONE_REGISTER
    user.save()
    UserStat.objects.add_stat(request, user.id, user_created=True)
    return {
        "token": token.create_token(user),
        "user": user.full()
    }


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["username", "password"])
def login(request):
    """
    @api {post} /authe/login/ Login method
    @apiName login
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} username Username of user, must be an email.
    @apiParam {String} password Password of user, minimum length: 6.
    @apiSuccess {Object} result Json representation of user with token.
    """
    try:
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        user = None
        try:
            validate_email(username)
            user = User.objects.filter(email=username).first()
        except:
            try:
                phone_object = phonenumbers.parse(username, None)
                if phonenumbers.is_valid_number(phone_object):
                    user = User.objects.filter(phone=username).first()
            except:
                return http.code_response(code=codes.INVALID_USERNAME,
                                          message=messages.INVALID_USERNAME)
        if user is None:
            return http.code_response(code=codes.USERNAME_NOT_FOUND,
                                      message=messages.USER_NOT_FOUND)
        if not user.is_active:
            return http.code_response(code=codes.USER_NOT_VERIFIED,
                                      message=messages.USER_NOT_VERIFIED)

        user = authenticate(username=user.username, password=password)

        if user is None:
            return http.code_response(
                code=codes.INCORRECT_USERNAME_OR_PASSWORD,
                message=messages.INCORRECT_USERNAME_OR_PASSWORD)

        user.timestamp = time_utils.get_timestamp_in_milli()
        user.save()
        return {
            'token': token.create_token(user),
            'user': user.full()
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
def account_activate(request, key):
    """
    User email activation.
    """
    try:
        template = "front/email_redirect.html"
        params = {}
        try:
            key = Activation.objects.get(key=key)
        except Exception as e:
            logger.warning(e)
            params["redirect_url"] = settings.FRONT_URL
            params["message"] = u"Ключ активации не найден"
            return render(request, template, params)
        user = User.objects.get(email=key.username)
        if key.is_active:
            user.is_active = True
            user.email_activated = True
            user.user_type = EMAIL_REGISTER
            key.is_active = False
            key.save()
            user.save()
            UserStat.objects.add_stat(request, user.id, user_created=True)
            params["redirect_url"] = settings.FRONT_AUTH_URL
            params["message"] = u"Аккаунт успешно активирован"
            return render(request, template, params)
        else:
            if user.is_active:
                params["redirect_url"] = settings.FRONT_URL
                params["message"] = u"Этот аккаунт уже активирован"
                return render(request, template, params)
            else:
                params["redirect_url"] = settings.FRONT_URL
                params["message"] = u"""Похоже на то, что ключ активации был
                                        отправлен несколько раз. Пожалуйста
                                        воспользуйтесь самой последней
                                        ссылкой"""
                return render(request, template, params)
    except Exception as e:
        logger.error(e)
        return HttpResponse(str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["access_token"])
def facebook_login(request):
    """
    @api {post} /api/authe/facebook_login/ Facebook login method
    @apiName facebook_login
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} access_token Access token of facebook user.
    @apiSuccess {Object} result Json representation of user with token.
    """
    try:
        access_token = request.POST['access_token']
        user = None
        info = oauth.get_facebook_info(access_token)

        if info is None:
            return http.code_response(code=codes.FB_OAUTH_TOKEN_INVALID,
                                      message=messages.FB_OAUTH_TOKEN_INVALID)
        if 'id' not in info:
            return http.code_response(code=codes.FB_OAUTH_TOKEN_INVALID,
                                      message=messages.FB_OAUTH_TOKEN_INVALID)

        full_name = info.get('name', None)
        email = info.get('email', None)
        fb_id = info['id']

        if email:
            user, created = User.objects.get_or_create(username=email)
            user.fb_id = fb_id
            user.email = email
            user.email_activated = True
            user.user_type = FACEBOOK_REGISTER
            if created:
                user.is_active = True
                user.user_type = FACEBOOK_REGISTER
            elif not user.is_active:
                user.user_type = FACEBOOK_REGISTER
                user.is_active = True
                # for security purposes
                user.set_password(password.generate_password(
                    length=settings.PASSWORD_LENGTH))
        else:
            try:
                user = User.objects.get(fb_id=fb_id)
                user.user_type = FACEBOOK_REGISTER
            except:
                random_username = (password.generate_password(length=20)
                                   + str(time_utils.get_timestamp_in_milli()))
                user = User.objects.create(username=random_username,
                                           fb_id=fb_id, is_active=True)
                user.user_type = FACEBOOK_REGISTER
                UserStat.objects.add_stat(request, user.id, user_created=True)

        if full_name and (user.full_name == "" or not user.full_name):
            user.full_name = full_name

        if not user.avatar or user.avatar is None:
            fb_avatar_name, fb_avatar_content = oauth.get_facebook_avatar(
                fb_id)
            if fb_avatar_name and fb_avatar_content:
                user.avatar.save(fb_avatar_name, File(
                    open(fb_avatar_content[0])), save=True)
                user.save()
        user.timestamp = time_utils.get_timestamp_in_milli()
        user.save()
        return {
            'token': token.create_token(user),
            'user': user.full()
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["username"])
def reset_password(request):
    """
    @api {post} /api/authe/reset/ Reset password method
    @apiName reset_password
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} username Email of user CHOSEN ON REGISTRATION.
    @apiSuccess {Object} result Json with code.
    """
    try:
        try:
            validate_email(request.POST["username"])
        except:
            return http.code_response(code=codes.INVALID_USERNAME,
                                      message=messages.INVALID_USERNAME)
        try:
            user = User.objects.get(email=request.POST['username'])
        except:
            return http.code_response(code=codes.USERNAME_NOT_FOUND,
                                      message=messages.USER_NOT_FOUND_EMAIL)
        token = str(user.id) + password.generate_password(length=30)
        ResetPasswordRequest.objects.create(user=user, token=token)
        try:
            user.email_reset_password(token=token)
        except Exception as e:
            logger.error(e)
            return http.code_response(code=codes.EMAIL_SERVICE_ERROR,
                                      message=messages.EMAIL_SERVICE_ERROR)
        return http.ok_response()
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["current_password", "new_password"])
@http.requires_token()
def change_password(request, user):
    """
    @api {post} /authe/change_password/ Change password method
    @apiName change_password
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} current_password Current password of user.
    @apiParam {String} new_password New password of user.
    @apiSuccess {Object} result Json with response code.
    """
    try:
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        if not user.check_password(current_password):
            return http.code_response(
                code=codes.INCORRECT_CURRENT_PASSWORD,
                message=messages.INCORRECT_CURRENT_PASSWORD)
        if len(new_password) < settings.PASSWORD_LENGTH:
            return http.code_response(
                code=codes.PASSWORD_LENGTH_ERROR,
                message=messages.PASSWORD_LENGTH_ERROR.format(
                    len(new_password)))
        user.set_password(new_password)
        user.save()
        return http.ok_response()
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(['token', 'new_password'])
def set_password_by_code(request):
    """
    Allows user to change password via token sent to email
    @api {post} /authe/reset_password/ Reset password via emailed token
    @apiName set_password_by_code
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} token emailed to user to reset password (get from url)
    @apiParam {String} new_password new password
    @apiSuccess {Object} result Json with code.
    """
    try:
        try:
            reset_request = ResetPasswordRequest.objects.get(
                token=request.POST["token"], deleted=False)
        except:
            return http.code_response(code=codes.RESET_CODE_NOT_FOUND,
                                      message=messages.RESET_CODE_NOT_FOUND)

        new_password = request.POST["new_password"]
        if len(new_password) < settings.PASSWORD_LENGTH:
            return http.code_response(
                code=codes.PASSWORD_LENGTH_ERROR,
                message=messages.PASSWORD_LENGTH_ERROR.format(
                    len(new_password)))
        reset_request.user.set_password(new_password)
        reset_request.user.save()
        reset_request.deleted = True
        reset_request.save()
        return {
            'token': token.create_token(reset_request.user),
            'user': reset_request.user.full()
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(['token'])
def activate_account_by_token(request):
    """
    Activates account via token sent to email
    @api {post} /authe/activate_account_by_token/ Activates account via token sent to email
    @apiName activate_account_by_token
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} token emailed to user to activate account (get from url)
    @apiSuccess {Object} result Json with code.
    """
    try:
        try:
            key = Activation.objects.get(key=request.POST["token"])
        except:
            return http.code_response(
                code=codes.ACTIVATION_CODE_NOT_FOUND,
                message=messages.ACTIVATION_CODE_NOT_FOUND)

        user = User.objects.get(email=key.username)

        if user.is_active:
            return http.code_response(code=codes.EMAIL_ACTIVATED,
                                      message=messages.EMAIL_ACTIVATED)
        if not key.is_active:
            return http.code_response(code=codes.ACTIVATION_TIME_EXPIRED,
                                      message=messages.ACTIVATION_TIME_EXPIRED)

        user.is_active = True
        user.email_activated = True
        key.is_active = False
        key.save()
        user.save()
        UserStat.objects.add_stat(request, user.id, user_created=True)
        return {
            "user": user.full(),
            "token": token.create_token(user)
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


def sms_redirect(request):
    """
    """
    return redirect('http://10.1.2.30:8002')


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["login"])
def check_login(request):
    """
    @api {post} /authe/login/check/ Check login
    @apiName check_login
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} login login to check
    @apiSuccess {Object} result Json with response code.
    """
    try:
        login = request.POST["login"]
        exists = False
        try:
            validate_email(login)
            exists = User.objects.filter(email=login, is_active=True).exists()
        except:
            try:
                phone_object = phonenumbers.parse(login, None)
                if phonenumbers.is_valid_number(phone_object):
                    exists = User.objects.filter(phone=login).exists()
            except:
                return http.code_response(code=codes.INVALID_USERNAME,
                                          message=messages.INVALID_USERNAME)
        return {
            "exists": exists
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.requires_token_with_extraction()
def logout(request, user, token_string):
    """
    @api {post} /authe/logout/ Logout method
    @apiName logout
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiSuccess {Object} result Json with response code.
    """
    try:
        if token.delete_token(token_string):
            return http.ok_response()
        else:
            return http.code_response(code=codes.TOKEN_INVALID,
                                      message=messages.TOKEN_INVALID)
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.require_http_methods("POST")
@http.required_parameters(["type"])
def get_csrf(request):
    """
    @api {post} /authe/csrf/ Get csrf
    @apiName get_csrf
    @apiGroup Authe
    @apiParam {String} type "m"/"w" WeB or mobile
    @apiSuccess {Object} result Json with response code.
    """
    try:
        return {
            "csrf_token": token.generate_csrf(request.POST["type"])
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["csrf_token"])
def verify_csrf(request):
    """
    @api {post} /authe/csrf/verify/ Verify csrf
    @apiName verify_csrf
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} csrf_token token
    @apiSuccess {Object} result Json with response code.
    """
    try:
        return {
            "verified": token.verify_csrf_token(request.POST["csrf_token"])
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))
