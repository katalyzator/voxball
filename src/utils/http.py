# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponse
from functools import wraps
import codes
import token
import json
import messages
import string_utils
from Constants import YEAR

User = get_user_model()


def extract_token_from_request(request):
    """
    Extracts token string from request. First tries to get it from AUTH_TOKEN
    header, if not found (or empty) tries to get from cookie.
    :param request:
    :return: Token string found in header or cookie; null otherwise.
    """
    header_names_list = settings.AUTH_TOKEN_HEADER_NAME
    token_string = None
    for name in header_names_list:
        if name in request.META:
            token_string = string_utils.empty_to_none(request.META[name])

    if token_string is None:
        if settings.AUTH_TOKEN_COOKIE_NAME in request.COOKIES:
            token_string = string_utils.empty_to_none(request.COOKIES[
                settings.AUTH_TOKEN_COOKIE_NAME])

    if token_string is None:
        if settings.AUTH_TOKEN_POST_NAME in request.POST:
            token_string = string_utils.empty_to_none(request.POST[
                settings.AUTH_TOKEN_POST_NAME])

    return string_utils.empty_to_none(token_string)


def extract_cookie_from_request(request):
    """
    Extracts user cookie string from request. Tries get it from cookie.
    :param request:
    :return: user_cookie string found in cookie; null otherwise.
    """
    user_cookie_string = request.COOKIES.get(settings.USER_COOKIE_NAME, None)
    if not user_cookie_string:
        user_cookie_string = request.META.get(settings.USER_COOKIE_HEADER_NAME)
    return string_utils.empty_to_none(user_cookie_string)


def required_parameters(parameters_list):
    """
    Decorator to make a view only accept request with required parameters.
    :param parameters_list: list of required parameters.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method == "POST":
                for parameter in parameters_list:
                    value = (
                        string_utils.empty_to_none(request.POST.get(parameter)
                                                   or request.FILES.get(parameter)))
                    if value is None:
                        return code_response(
                            codes.MISSING_REQUIRED_PARAMS,
                            messages.MISSING_REQUIRED_PARAMS.format(parameter))
            else:
                for parameter in parameters_list:
                    value = string_utils.empty_to_none(
                        request.GET.get(parameter))
                    if value is None:
                        return code_response(
                            codes.MISSING_REQUIRED_PARAMS,
                            messages.MISSING_REQUIRED_PARAMS.format(parameter))

            return func(request, *args, **kwargs)
        return inner
    return decorator


def require_http_methods(param):
    """
    Decorator to make a view only accept request with required http method.
    :param required http method.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method != param:
                return code_response(codes.INCORRECT_HTTP_METHOD, param)
            return func(request, *args, **kwargs)
        return inner
    return decorator


def moderators_token():
    """
    Decorator to make a view only accept request with valid token.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, user, *args, **kwargs):
            if not user.is_moderator:
                return code_response(codes.PERMISSION_DENIED)
            return func(request, user, *args, **kwargs)
        return inner
    return decorator


def requires_token():
    """
    Decorator to make a view only accept request with valid token.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):

            token_string = extract_token_from_request(request)
            if token_string is None:
                return code_response(codes.BAD_REQUEST,
                                     messages.TOKEN_INVALID)

            user = token.verify_token(token_string)
            if user is None:
                return code_response(codes.TOKEN_INVALID,
                                     messages.TOKEN_INVALID)

            return func(request, user, *args, **kwargs)
        return inner
    return decorator


def requires_token_with_extraction():
    """
    Decorator to make a view only accept request with valid token and extracting token_string.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            token_string = extract_token_from_request(request)
            if token_string is None:
                return code_response(codes.BAD_REQUEST,
                                     messages.TOKEN_NOT_FOUND)

            user = token.verify_token(token_string)
            if user is None:
                return code_response(codes.TOKEN_INVALID,
                                     messages.TOKEN_INVALID)

            return func(request, user, token_string, *args, **kwargs)
        return inner
    return decorator


def requires_cookie_or_token():
    """
    Decorator to make a view only accept request with valid token or cookie.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            token_string = extract_token_from_request(request)
            cookie_string = extract_cookie_from_request(request)

            if token_string is None and cookie_string is None:
                return code_response(
                    codes.BAD_REQUEST,
                    messages.MISSING_REQUIRED_PARAMS.format("token or cookie"))

            user = None
            if token_string:
                user = token.verify_token(token_string)

            return func(request, user, cookie_string, *args, **kwargs)
        return inner
    return decorator


def extract_token_or_cookie_from_request():
    """
    Decorator to extract token or cookie or both of them
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            token_string = extract_token_from_request(request)
            cookie_string = extract_cookie_from_request(request)

            user = None
            if token_string:
                user = token.verify_token(token_string)

            return func(request, user, cookie_string, *args, **kwargs)
        return inner
    return decorator


def http_response_with_json_body(body):
    return HttpResponse(body, content_type="application/json")


def http_response_with_json(json_object):
    return http_response_with_json_body(json.dumps(json_object))


def json_response():
    """
    Decorator that wraps response into json.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            response = func(request, *args, **kwargs)
            if not ('code' in response):
                response['code'] = codes.OK
            response = http_response_with_json(response)
            if (settings.USER_COOKIE_NAME not in request.COOKIES
                    or request.COOKIES.get(settings.USER_COOKIE_NAME)
                    in ["", None]):
                cookie = token.generate_cookie()
                if request.META.get(settings.USER_COOKIE_HEADER_NAME):
                    cookie = request.META[settings.USER_COOKIE_HEADER_NAME]
                response.set_cookie(settings.USER_COOKIE_NAME, cookie, max_age=YEAR)
            return response
        return inner
    return decorator


def code_response(code, message=None, errors=None):
    result = {'code': code}
    if message:
        result['message'] = message
    if errors:
        result['errors'] = errors
    return result


def ok_response():
    return code_response(codes.OK)


def verify_csrf():
    """
    Decorator to that protects from csrf
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if settings.CSRF_ON:
                if settings.CSRF_TOKEN_HEADER_NAME not in request.META:
                    return code_response(code=codes.CSRF_INVALID,
                                         message=messages.CSRF_INVALID)
                csrf_token = request.META[settings.CSRF_TOKEN_HEADER_NAME]
                if not token.verify_csrf_token(csrf_token):
                    return code_response(code=codes.CSRF_INVALID,
                                         message=messages.CSRF_INVALID)
            return func(request, *args, **kwargs)
        return inner
    return decorator


def json_http_repsonse():
    """
    Decorator that return json / http response
    """
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            response = func(*args, **kwargs)
            if isinstance(response, dict):
                return http_response_with_json(response)
            return response
        return inner
    return decorator


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
