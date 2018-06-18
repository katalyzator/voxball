# -*- coding: utf-8 -*-
from authe import tasks
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone
from authe.models import Activation, ResetEmailRequest
from polls.models import Category, UserCategory
from utils import codes, messages, http, token, password
from utils.image_utils import get_resized_image
import logging
import phonenumbers
import uuid


logger = logging.getLogger(__name__)
User = get_user_model()


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.requires_token()
def update_profile(request, user):
    """
    @api {post} /authe/update_profile/ Updates profile of user
    @apiName activate_email
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} email New email for user [optional].
    @apiParam {String} phone New phone for user [optional].
    @apiParam {String} send_push "true"/"false" [optional].
    @apiParam {Number} city_id Id of city [optional].
    @apiParam {String} full_name New full name for user [optional].
    @apiParam {String} delete_avatar Delete avatar? "true" or "false" [optional].
    @apiParam {Object} avatar Avatar of user, must be an image [optional].
    @apiParam {Number} category_ids[] IDs of User Categories
    @apiParam {Number} top Top of resized image.
    @apiParam {Number} left Left of resized image.
    @apiParam {Number} width Width of resized image.
    @apiParam {Number} height Height of resized image.
    @apiParam {String} resize Resize avatar? "true" or "false" [optional].
    @apiSuccess {Object} result Json with response code.
    """
    try:
        logger.info("POST data: {0}".format(request.POST))
        updated_fields = []
        """Updating email"""
        email = request.POST.get("email", "")
        if email and email != user.email:
            updated_fields.append("email")
            _code, _message = change_or_set_email(request, user, email)
            if _code != codes.OK:
                return http.code_response(code=_code,
                                          message=_message)

        if user.profile_type == 1:
            if 'partner_type' in request.POST:
                user.partner_type = 1 if request.POST['partner_type'] in [1, '1'] else 0

            if 'partner_details' in request.POST:
                user.partner_details = request.POST['partner_details']

            if 'partner_author' in request.POST:
                user.partner_author = request.POST['partner_author']

            if 'partner_phone' in request.POST:
                user.partner_phone = request.POST['partner_phone']

        phone = request.POST.get("phone", "")
        if phone and user.phone != phone:
            updated_fields.append("phone")
            _code, _message = change_or_set_phone(phone)
            if _code != codes.OK:
                return http.code_response(code=_code,
                                          message=_message)

        if 'full_name' in request.POST:
            updated_fields.append('full_name')
            user.full_name = request.POST['full_name']

        if request.POST.get("city_id"):
            try:
                user.city_id = int(request.POST['city_id'])
            except Exception as e:
                logger.error(e)
                return http.code_response(code=codes.INVALID_CITY,
                                          message=messages.INVALID_CITY)

        """Updating avatar"""
        if 'avatar' in request.FILES:
            top = int(request.POST.get("top", 0))
            left = int(request.POST.get("left", 0))
            width = int(request.POST.get("width",
                                         settings.POLL_AVATAR_SIZE[0]))
            height = int(request.POST.get("height",
                                          settings.POLL_AVATAR_SIZE[1]))
            image = request.FILES.get('avatar', None)
            updated_fields.append('avatar')
            try:
                # user.avatar = (get_resized_image(image, left, top, width,
                #                                  height,
                #                                  settings.POLL_AVATAR_SIZE)
                #                if request.POST.get("resize", "false") == "true"
                #                and image else image)
                user.avatar.save(str(uuid.uuid4())+'.jpg', get_resized_image(image, left, top, width,
                                                 height,
                                                 settings.POLL_AVATAR_SIZE)
                               if request.POST.get("resize", "false") == "true"
                               and image else image)
                user.avatar_width = width
                user.avatar_height = height
                user.save()
            except Exception as e:
                logger.error(e)
                return http.code_response(code=codes.WRONG_AVATAR_FORMAT,
                                          message=messages.WRONG_AVATAR_FORMAT)
        if request.POST.get('delete_avatar', 'false') == 'true':
            user.avatar = None
            updated_fields.append('delete_avatar')

        """Updating user category"""
        if request.POST.get('update_categories', False):
            updated_fields.append('category_ids[]')
            category_ids = request.POST.getlist("category_ids[]")
            if len(category_ids) != Category.objects.filter(id__in=category_ids,
                                                            is_active=True).count():
                return http.code_response(
                    code=codes.CATEGORIES_DOESNT_MATCH,
                    message=messages.CATEGORIES_DOESNT_MATCH)
            UserCategory.objects.add_categories(user, category_ids)

        if request.POST.get("send_push"):
            user.push = request.POST["send_push"] == "true"

        user.save()
        updated_fields = ','.join(updated_fields)
        return {
            'user': user.full()
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.require_http_methods("GET")
@http.requires_token()
def get_user(request, user):
    """
    @api {get} /authe/get_user/ Get profile of user
    @apiName get_user
    @apiGroup Authe
    @apiHeader {String} Auth-Token Authentication token.
    @apiSuccess {Object} result Json with response code.
    """
    try:
        return {
            'user': user.full(),
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
def get_users(request):
    """
    @api {post} /authe/get_users/ Get profile of user
    @apiName get_user
    @apiGroup Authe
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} tokens[] Token of user
    @apiParam {String} tokens[] Token of user
    @apiSuccess {Object} result Json with response code.
    """
    try:
        logger.info("post: {0}".format(request.POST))
        tokens = request.POST.getlist('tokens[]')
        users = []
        for user_token in tokens:
            user = token.verify_token(user_token)
            if user is None:
                users.append(None)
            else:
                users.append({
                    'token': user_token,
                    'user': user.full()
                    })
        return {
            'result': users
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(["category_ids[]"])
def update_user_categories(request, user):
    """
    @api {post} /authe/profile/categories/ Add or delete categories of user
    @apiName update_user_categories
    @apiGroup Auth
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} category_ids[] IDs of categories
    @apiSuccess {Json} result Json representation of polls.
    """
    try:
        category_ids = request.POST.getlist("category_ids[]")
        if len(category_ids) != Category.objects.filter(id__in=category_ids,
                                                        is_active=True).count():
            return http.code_response(code=codes.CATEGORIES_DOESNT_MATCH,
                                      message=messages.CATEGORIES_DOESNT_MATCH)
        UserCategory.objects.add_categories(user, category_ids)
        return http.ok_response()
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(["category_id"])
def add_delete_category(request, user):
    """
    @api {post} /authe/profile/category/add_delete/ Add or delete category of user
    @apiName add_delete_category
    @apiGroup Auth
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} category_id ID of category
    @apiSuccess {Json} result Json representation of polls.
    """
    try:
        try:
            category = Category.objects.get(id=request.POST["category_id"])
        except:
            return http.code_response(code=codes.CATEGORY_NOT_FOUND,
                                      message=messages.CATEGORY_NOT_FOUND)
        user_category, created = UserCategory.objects.get_or_create(user=user,
                                                                    category=category)
        if not created:
            user_category.is_active = not user_category.is_active
            user_category.save()
        return http.ok_response()
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


def change_or_set_email(request, user, email):
    try:
        try:
            validate_email(email)
        except Exception as e:
            return codes.BAD_EMAIL, messages.BAD_EMAIL.format(email)

        if User.objects.filter(email=email, is_active=True).exists():
            return codes.USERNAME_USED, messages.USERNAME_USED

        key = ResetEmailRequest.objects.generate(new_email=email, user=user)
        link = settings.SITE_URL + reverse('authe:activate_new_email', args=[key])
        tasks.email(
            to=email,
            subject=messages.RESET_EMAIL_ACTIVATION,
            message=render_to_string('emails/activate_new_email.html',
                                     context={'key': key, 'link': link},
                                     request=request))
        return codes.OK, ""
    except Exception as e:
        logger.error(e)
        return codes.EMAIL_SERVICE_ERROR, messages.EMAIL_SERVICE_ERROR


def change_or_set_phone(phone):
    try:
        try:
            phone_object = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(phone_object):
                return codes.PHONE_INCORRECT, messages.PHONE_INCORRECT
        except Exception as e:
            return codes.PHONE_INCORRECT, messages.PHONE_INCORRECT

        if User.objects.filter(phone=phone, is_active=True).exists():
            return codes.PHONE_USED, messages.PHONE_USED
        else:
            code = password.generate_sms_code()
            Activation.objects.generate(username=phone, code=code)
            tasks.send_message(
                phone, settings.SMS_ACTIVATION_TEXT.format(password=code))
            return codes.OK, ""
    except Exception as e:
        logger.error(e)
        return codes.EMAIL_SERVICE_ERROR, messages.EMAIL_SERVICE_ERROR


@csrf_exempt
def activate_new_email(request, key):
    """
    User new email activation.
    """
    try:
        template = "front/email_redirect.html"
        params = {}
        try:
            key = ResetEmailRequest.objects.get(key=key, is_active=True)
        except Exception as e:
            logger.warning(e)
            params["redirect_url"] = settings.FRONT_URL
            params["message"] = u"Ключ активации не найден"
            return render(request, template, params)
        user = key.user
        if key.is_active:
            if User.objects.filter(email=key.new_email,
                                   is_active=True).exists():
                params["redirect_url"] = settings.FRONT_URL
                params["message"] = u"""Извиняемся, но имя пользователя уже
                                        занято"""
                return render(request, template, params)
            if user.email:
                tasks.email(to=user.email,
                                  subject=messages.RESET_EMAIL_DEACTIVATION,
                                  message="")
            try:
                validate_email(user.username)
                user.username = key.new_email
            except:
                pass
            user.email = key.new_email
            user.email_activated = True
            key.is_active = False
            key.save()
            user.save()
            params["redirect_url"] = settings.FRONT_URL
            params["message"] = u"E-mail успешно изменен"
            return render(request, template, params)
        else:
            params["redirect_url"] = settings.FRONT_URL
            params["message"] = u"Ссылка устарела"
            return render(request, template, params)
    except Exception as e:
        logger.error(e)
        return HttpResponse(str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["code"])
@http.requires_token()
def activate_new_phone(request, user):
    """
    @api {post} /authe/profile/activate_new_phone/ Activate new phone
    @apiName activate_new_phone
    @apiGroup Profile
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} code Code sent to user.
    @apiSuccess {Object} Json with code
    """
    try:
        code = request.POST["code"]
        now = timezone.now()
        try:
            activation = Activation.objects.get(
                code=code, is_active=True)
        except:
            return http.code_response(
                code=codes.ACTIVATION_CODE_NOT_FOUND,
                message=messages.ACTIVATION_CODE_NOT_FOUND)
        if User.objects.filter(phone=activation.username, is_active=True).exists():
            return http.code_response(code=codes.PHONE_USED,
                                      message=messages.PHONE_USED)
        if activation.end_time < now:
            return http.code_response(
                code=codes.ACTIVATION_TIME_EXPIRED,
                message=messages.ACTIVATION_TIME_EXPIRED)
        activation.is_active = False
        activation.save()
        user.phone = activation.username
        try:
            phone_object = phonenumbers.parse(user.username, None)
            if phonenumbers.is_valid_number(phone_object):
                user.username = activation.username
        except:
            pass
        user.save()
        return {
            "token": token.create_token(user),
            "user": user.full()
        }
    except Exception as e:
        logger.error(e)
        return http.code_response(codes.SERVER_ERROR, str(e))
