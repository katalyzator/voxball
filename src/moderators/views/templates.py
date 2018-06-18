# -*- coding: utf-8 -*-
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from moderators.models import PollTemplate, PollChoiceTemplate, \
    PollTemplateCategory
from polls.models import PollKeyword, Category, Poll
from utils.string_utils import json_list_from_string_list, integer_list
from utils.time_utils import get_datetime_from_timestamp
from utils import codes, messages, http, Constants, image_utils
import datetime
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.moderators_token()
@http.require_http_methods("POST")
@http.required_parameters(['title', 'poll_type', 'date_begin', 'date_end'])
def create(request, user):
    """
    @api {post} /moderators/template/create/ PollTemplate creation method
    @apiName create
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} title Title of poll.
    @apiParam {Image} image Image for file.
    @apiParam {Number} poll_type 0 - Rating scale,
                                 1 - Single choice,
                                 2 - Multiple choice.
    @apiParam {Number} date_begin unix timestamp in millisecs.
    @apiParam {Number} date_end  unix timestamp in millisecs.
    @apiParam {String-json} min_value  Bad
    @apiParam {String-json} max_value  Good
    @apiParam {String-json[]} sc_choices[]  [{"value":"123123", "priority":"123"}].
    @apiParam {Number[]} category_ids[]  [1, 2, 3].
    @apiParam {String[]} keywords[] [football, keyword, Juventus].
    @apiSuccess {Json} result Json representation of poll.
    @apiParam {String} resize (optional) - "true"/"false"
    @apiParam {Number} left (required if resize)
    @apiParam {Number} top (required if resize)
    @apiParam {Number} width (required if resize)
    @apiParam {Number} height (required if resize)
    """
    try:
        try:
            title = request.POST['title']
            poll_type = int(request.POST['poll_type'])
            date_begin = int(request.POST['date_begin'])
            date_end = int(request.POST['date_end'])
            min_value = request.POST.get("min_value")
            max_value = request.POST.get("max_value")
            sc_choices = json_list_from_string_list(
                request.POST.getlist('sc_choices[]'))
            category_ids = integer_list(request.POST.getlist("category_ids[]"))
            keywords = request.POST.getlist("keywords[]")
            image = request.FILES.get("image")
        except Exception as exc:
            logger.error(exc)
            return http.code_response(code=codes.INVALID_PARAMETERS,
                                      message=messages.INVALID_PARAMETERS)

        """validation"""
        if len(category_ids) and \
           len(category_ids) != Category.objects.filter(id__in=category_ids,
                                                        is_active=True).count():
            return http.code_response(
                code=codes.CATEGORIES_DOESNT_MATCH,
                message=messages.CATEGORIES_DOESNT_MATCH)
        """end validation"""

        # TODO: add threshold
        if get_datetime_from_timestamp(date_begin).date() < datetime.date.today() or date_end < date_begin:
            return http.code_response(codes.INVALID_DATES,
                                      message=messages.INVALID_DATES)
        if poll_type not in [p[0] for p in PollTemplate.TYPES]:
            return http.code_response(codes.INVALID_POLL_TYPE,
                                      message=messages.INVALID_POLL_TYPE)

        if request.POST.get("resize", "false") == "true" and image:
            image = image_utils.get_resized_image(
                image=image,
                left=int(request.POST.get("left", 0)),
                top=int(request.POST.get("top", 0)),
                width=int(request.POST.get(
                    "width", settings.POLL_IMG_SIZE[0])),
                height=int(request.POST.get("height", settings.POLL_IMG_SIZE[1])))

        with transaction.atomic():
            new_poll = PollTemplate.objects.create(
                user=user,
                title=title,
                poll_type=poll_type,
                date_begin=date_begin,
                date_end=date_end,
                min_value=min_value,
                max_value=max_value,
                image=image,
                category_ids=category_ids,
                is_template=True)
            if poll_type == PollTemplate.RATING_SCALE:
                PollChoiceTemplate.objects.create_rs_choices(poll=new_poll)
            else:
                if len(sc_choices) < Constants.SINGLE_CHOICE_MIN_COUNT:
                    return http.code_response(
                        code=codes.SC_COUNT_INVALID,
                        message=messages.SC_COUNT_INVALID)
                PollChoiceTemplate.objects.create_sc_choices(
                    poll=new_poll, choices=sc_choices)
            PollTemplateCategory.objects.add_categories(
                poll=new_poll, categories=Category.objects.filter(
                    id__in=category_ids, is_active=True))
            PollKeyword.objects.add_keywords(poll=new_poll, keywords=keywords)
        return {
            "result": new_poll.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
def read(request):
    """
    @api {post} /moderators/template/read/ PollTemplate read method
    @apiName read
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiParam {String} poll_id id of poll.
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = PollTemplate.objects.get(id=request.POST["poll_id"])
        except:
            return http.code_response(codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        return {
            "result": poll.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.moderators_token()
@http.required_parameters(['poll_id', 'poll_type', 'date_begin', 'date_end'])
@http.require_http_methods("POST")
def update(request, user):
    """
    @api {post} /moderators/template/update/ PollTemplate update method
    @apiName update
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} title Title of poll.
    @apiParam {Number} date_begin unix timestamp in millisecs.
    @apiParam {Number} date_end  unix timestamp in millisecs.
    @apiParam {String-json} min_value  Bad
    @apiParam {String-json} max_value  Good
    @apiParam {String-json[]} sc_choices[]  [{"value":"123123",
                                              "priority":"123"}].
    @apiParam {Number[]} category_ids[]  [1, 2, 3].
    @apiParam {String[]} keywords[] [football, keyword, Juventus].
    @apiParam {String} resize (optional) - "true"/"false"
    @apiParam {Number} left (required if resize)
    @apiParam {Number} top (required if resize)
    @apiParam {Number} width (required if resize)
    @apiParam {Number} height (required if resize)
    @apiParam {Number} poll_type 1 - Single choice,
                                 2 - Multiple choice.
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            title = request.POST.get('title')
            date_begin = int(request.POST['date_begin'])
            date_end = int(request.POST['date_end'])
            sc_choices = json_list_from_string_list(
                request.POST.getlist('sc_choices[]'))
            category_ids = integer_list(request.POST.getlist("category_ids[]"))
            keywords = request.POST.getlist("keywords[]")
            image = request.FILES.get("image")
            poll_type = int(request.POST["poll_type"])
        except Exception as exc:
            logger.error(exc)
            return http.code_response(codes.INVALID_PARAMETERS,
                                      message=messages.INVALID_PARAMETERS)
        try:
            poll = PollTemplate.objects.get(id=request.POST['poll_id'],
                                            user=user)
        except:
            return http.code_response(codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        if (get_datetime_from_timestamp(date_begin).date()
                < datetime.date.today() or date_end < date_begin):
            return http.code_response(codes.INVALID_DATES,
                                      messages.INVALID_DATES)
        poll.title = title
        poll.date_begin = date_begin
        poll.date_end = date_end
        poll.min_value = request.POST.get("min_value")
        poll.max_value = request.POST.get("max_value")
        if poll_type != Poll.RATING_SCALE:
            poll.poll_type = poll_type

        if request.POST.get("resize", "false") == "true" and image:
            image = image_utils.get_resized_image(
                image=image, left=int(request.POST.get("left", 0)),
                top=int(request.POST.get("top", 0)),
                width=int(request.POST.get(
                    "width", settings.POLL_IMG_SIZE[0])),
                height=int(request.POST.get(
                    "height", settings.POLL_IMG_SIZE[1])))

        if image:
            poll.image = image

        PollChoiceTemplate.objects.filter(poll=poll).update(is_active=False)
        PollChoiceTemplate.objects.create_sc_choices(poll=poll,
                                                     choices=sc_choices)
        poll.save()
        PollTemplateCategory.objects.add_categories(
            poll=poll, categories=Category.objects.filter(id__in=category_ids,
                                                          is_active=True))
        PollKeyword.objects.add_keywords(poll=poll, keywords=keywords)
        return {
            "result": poll.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.moderators_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id'])
def delete(request, user):
    """
    @api {post} /moderators/template/delete/ PollTemplate delete method
    @apiName delete
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} poll_id Id of poll.
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = PollTemplate.objects.get(id=request.POST['poll_id'],
                                            user=user)
        except Exception as exc:
            logger.error(exc)
            return http.code_response(codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        poll.is_active = False
        poll.save()
        return {
            "result": poll.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.moderators_token()
@http.require_http_methods("POST")
def feed(request, user):
    """
    @api {post} /moderators/template/feed/ PollTemplate feed method
    @apiName feed
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} timestamp Timestamp of poll.
    @apiParam {Number} limit Limit per request.
    @apiParam {Number[]} category_ids[] category id to filter.
    @apiSuccess {Json[]} result Json representation of polls.
    """
    try:
        try:
            timestamp = int(request.POST["timestamp"])
        except:
            timestamp = Constants.TIMESTAMP_MAX
        try:
            limit = int(request.POST['limit'])
        except:
            limit = Constants.FEED_LIMIT
        query = {"timestamp__lt": timestamp,
                 "is_active": True}
        if request.POST.getlist("category_ids[]"):
            category_ids = integer_list(request.POST.getlist("category_ids[]"))
            query["category_ids__overlap"] = category_ids
        polls = PollTemplate.objects.filter(**query).order_by(
            '-timestamp')[:limit]
        return {
            'result': [p.full() for p in polls]
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))
