# -*- coding: utf-8 -*-

import datetime, json
from django.views.decorators.csrf import csrf_exempt

from utils import http, token, codes, messages

from pushtoken.models import PushSender

@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["pushtoken"])
def subscribe(request):
    try:
        pushtoken = request.POST.get("pushtoken")
        dev_type = request.POST.get("type", '')
    except Exception as exc:
        return http.code_response(code=codes.INVALID_PARAMETERS,
                                    message=messages.INVALID_PARAMETERS)

    user = None
    user_id = 0
    token_string = http.extract_token_from_request(request)
    if token_string:
        user = token.verify_token(token_string)
        if user:
            user.push_notifications_enabled = True
            user.save()
            user_id = user.id


    open("/logs/push_info.logs", "a+").write("{}={}-{}-{}\n".format(datetime.datetime.now(), user_id, dev_type, pushtoken))

    return {
        'code': 0
    }


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(["status"])
def set_settings(request, user):
    try:
        status = request.POST.get("status")
    except Exception as exc:
        return http.code_response(code=codes.INVALID_PARAMETERS,
                                    message=messages.INVALID_PARAMETERS)

    user.push_notifications_enabled = status in ["1", "true", True]
    user.save()

    return {
        'code': 0
    }


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(["message", "payload"])
@http.requires_token()
@http.moderators_token()
def send_push(request, user):
    try:
        message = request.POST.get("message")
        url = json.loads(request.POST.get("payload"))["link"]
    except Exception as exc:
        return http.code_response(code=codes.INVALID_PARAMETERS,
                                    message=messages.INVALID_PARAMETERS)

    PushSender.objects.create(title=message, url=url)
    # open("/logs/push_info.logs", "a+").write("{}={}-status-{}\n".format(datetime.datetime.now(), user.id, status))
    # user.push_notifications_enabled = status in ["1", "true", True]
    # user.save()

    return {
        'code': 0
    }
