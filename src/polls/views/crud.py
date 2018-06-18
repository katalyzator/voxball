# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from authe.models import MainUser, get_cdn_url
from moderators.models import Article, PollTemplate
from polls import tasks
from polls.models import Poll, PollChoice, PollAnswer, PollCategory, \
    PollKeyword, Category, UserCategory, PollComment
from statistics.models import UserStat
from utils import codes, messages, http, Constants, image_utils, token
from utils.string_utils import json_list_from_string_list, \
    integer_list, handle_param
from utils.time_utils import get_timestamp_in_milli, \
    get_datetime_from_timestamp
import datetime
import logging
import os

logger = logging.getLogger(__name__)


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['title', 'poll_type', 'date_begin', 'date_end'])
def create(request, user):
    """
    @api {post} /polls/create/ Poll creation method
    @apiName create
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} title Title of poll.
    @apiParam {String} partner_url Partner url.
    @apiParam {Object} image Image for file.
    @apiParam {Number} poll_type 0 - Rating scale,
                                 1 - Single choice,
                                 2 - Multiple choice.
    @apiParam {Number} date_begin unix timestamp in millisecs.
    @apiParam {Number} date_end  unix timestamp in millisecs.
    @apiParam {json} min_value  Bad
    @apiParam {json} max_value  Good
    @apiParam {json[]} sc_choices[]  {"value":"123123", "priority":"123"}
    @apiParam {json[]} sc_choices[]  {"value":"123123", "priority":"123"}
    @apiParam {Number[]} category_ids[]  [1, 2, 3].
    @apiParam {String[]} keywords[] [football, keyword, Juventus].
    @apiParam {String} resize (optional) - "true"/"false"
    @apiParam {Number} left (required if resize)
    @apiParam {Number} top (required if resize)
    @apiParam {Number} width (required if resize)
    @apiParam {Number} height (required if resize)
    @apiParam {Number} template_id ID of template
    @apiParam {Number} category_id ID of category
    @apiSuccess {json} result Json representation of poll.
    """
    try:
        try:
            title = request.POST['title']
            poll_type = int(request.POST['poll_type'])
            date_begin = int(request.POST['date_begin'])
            date_end = int(request.POST['date_end'])
            min_value = request.POST.get("min_value")
            max_value = request.POST.get("max_value")
            partner_url = request.POST.get("partner_url", '')
            sc_choices = json_list_from_string_list(
                request.POST.getlist('sc_choices[]'))
            category_ids = integer_list(request.POST.getlist("category_ids[]"))
            keywords = request.POST.getlist("keywords[]")
            image = request.FILES.get("image")
            # get image of template if sent
            video = request.POST.get("video")
            comments_enabled = str(request.POST.get('comments_enabled'))
            private_post = str(request.POST.get("private_survey"))

            template_id = request.POST.get("template_id")
            category_id = handle_param(request.POST.get("category_id"), int)

            if comments_enabled == "true":
                comment_status = True
            else:
                comment_status = False

            if private_post == "true":
                private_survey = True
            else:
                private_survey = False

        except Exception as exc:
            return http.code_response(code=codes.INVALID_PARAMETERS,
                                      message=messages.INVALID_PARAMETERS)

        """validation"""
        if len(category_ids) and \
                        len(category_ids) != Category.objects.filter(
                    id__in=category_ids, is_active=True).count():
            return http.code_response(
                code=codes.CATEGORIES_DOESNT_MATCH,
                message=messages.CATEGORIES_DOESNT_MATCH)
        """end validation"""

        # TODO: add threshold
        if (get_datetime_from_timestamp(date_begin).date()
                < datetime.date.today()) or date_end < date_begin:
            return http.code_response(code=codes.INVALID_DATES,
                                      message=messages.INVALID_DATES)
        if poll_type not in [p[0] for p in Poll.TYPES]:
            return http.code_response(code=codes.INVALID_POLL_TYPE,
                                      message=messages.INVALID_POLL_TYPE)

        if request.POST.get("resize", "false") == "true" and image:
            image = image_utils.get_resized_image(
                image=image, left=int(request.POST.get("left", 0)),
                top=int(request.POST.get("top", 0)),
                width=int(request.POST.get(
                    "width", settings.POLL_IMG_SIZE[0])),
                height=int(request.POST.get(
                    "height", settings.POLL_IMG_SIZE[1])))

        if template_id:
            try:
                template = PollTemplate.objects.get(id=int(template_id))
                image = template.image
            except:
                return http.code_response(codes.TEMPLATE_NOT_FOUND,
                                          messages.TEMPLATE_NOT_FOUND)

        with transaction.atomic():
            path_to_default = os.path.join(settings.BASE_DIR,
                                           settings.DEFAULT_POLL_IMAGE_URL)
            facebook_image = image or File(open(path_to_default, 'r'))
            facebook_image = image_utils.get_texted_image(facebook_image,
                                                          title)
            choices_array = []
            if (poll_type == Poll.SINGLE_CHOICE
                or poll_type == Poll.MULTIPLE_CHOICE):
                for choice in sc_choices:
                    choices_array.append(choice['value'])
            new_poll = Poll.objects.create_poll(
                request=request, user=user, title=title,
                poll_type=poll_type, date_begin=date_begin,
                date_end=date_end, min_value=min_value,
                max_value=max_value, image=image,
                partner_url=partner_url,
                facebook_image=facebook_image,
                category_ids=category_ids, keywords_array=keywords,
                category_id=category_id,
                choices_array=choices_array, video=video, comment_status=comment_status, private_survey=private_survey)
            UserStat.objects.add_stat(request=request,
                                      user_id=user.id,
                                      poll_id=new_poll.id,
                                      poll_created=True)
            if poll_type == Poll.RATING_SCALE:
                PollChoice.objects.create_rs_choices(poll=new_poll)
            else:
                if len(sc_choices) < Constants.SINGLE_CHOICE_MIN_COUNT:
                    raise Exception(messages.SC_COUNT_INVALID)
                    return http.code_response(
                        code=codes.SC_COUNT_INVALID,
                        message=messages.SC_COUNT_INVALID)
                PollChoice.objects.create_sc_choices(poll=new_poll,
                                                     choices=sc_choices)
            PollCategory.objects.add_categories(
                poll=new_poll, categories=Category.objects.filter(
                    id__in=category_ids, is_active=True))
            PollKeyword.objects.add_keywords(poll=new_poll, keywords=keywords)
            user.increment_poll_count()
            now = get_timestamp_in_milli()
            delay = (date_begin - now) / 1000
            tasks.update_category_counters.apply_async(
                (new_poll.id, category_ids), countdown=delay)
        return {
            "result": new_poll.full(user, with_fb=True)
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=exc)


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.required_parameters(['poll_id', 'poll_type', 'date_begin', 'date_end'])
@http.require_http_methods("POST")
def update(request, user):
    """
    @api {post} /polls/update/ Poll update method
    @apiName update
    @apiGroup Polls
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
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            title = request.POST.get('title')
            date_begin = int(request.POST['date_begin'])
            date_end = int(request.POST['date_end'])
            min_value = request.POST.get("min_value")
            max_value = request.POST.get("max_value")
            sc_choices = json_list_from_string_list(
                request.POST.getlist('sc_choices[]'))
            category_ids = integer_list(request.POST.getlist("category_ids[]"))
            keywords = request.POST.getlist("keywords[]")
            video = request.POST.get("video")
            private_post = str(request.POST.get("private_survey"))
            comments_enabled = str(request.POST.get("comments_enabled"))
            if comments_enabled == "true":
                comment_status = True
            else:
                comment_status = False

            if private_post == "true":
                private_survey = True
            else:
                private_survey = False

        except Exception as exc:
            return http.code_response(codes.INVALID_PARAMETERS,
                                      message=messages.INVALID_PARAMETERS)
        try:
            poll = Poll.objects.get(id=request.POST['poll_id'], user=user)
        except:
            return http.code_response(codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        if get_datetime_from_timestamp(date_begin).date() < datetime.date.today() or date_end < date_begin:
            return http.code_response(codes.INVALID_DATES,
                                      message=messages.INVALID_DATES)
        poll.title = title
        poll.date_begin = date_begin
        poll.date_end = date_end
        poll.min_value = min_value
        poll.max_value = max_value
        poll.timestamp = get_timestamp_in_milli()
        poll.keywords = keywords
        poll.video = video
        poll.comment_status = comment_status
        poll.private_survey = private_survey
        if request.FILES.get("image"):
            poll.image = request.FILES.get("image")
        if poll.poll_type == Poll.RATING_SCALE:
            try:
                choice = PollChoice.objects.get(poll=poll)
            except:
                return http.code_response(codes.POLL_CHOICE_NOT_FOUND,
                                          messages.POLL_CHOICE_NOT_FOUND)
            PollChoice.objects.update_rs_choice(poll=poll, choice=choice,
                                                rs_choice=rs_choice)
        else:
            PollChoice.objects.update_sc_choices(poll=poll, choices=sc_choices)
        poll.save()
        PollCategory.objects.add_categories(poll=poll,
                                            categories=Category.objects.filter(id__in=category_ids, is_active=True))
        PollKeyword.objects.add_keywords(poll=poll, keywords=keywords)
        return {
            "result": poll.full(user=user)
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id'])
def delete(request, user):
    """
    @api {post} /polls/delete/ Poll delete method
    @apiName delete
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} poll_id Id of poll.
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = Poll.objects.get(id=request.POST['poll_id'], user=user)
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        poll.is_active = False
        poll.save()
        return {
            "result": poll.full(user=user)
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
@http.required_parameters(["poll_id"])
@http.require_http_methods("POST")
def read(request, user, cookie):
    """
    @api {post} /polls/read/ Poll read method
    @apiName read
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiHeader {String} user_cookie User cookie.
    @apiParam {String} poll_id id of poll.
    @apiParam {String} private_code Private code of poll
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = Poll.objects.get(id=request.POST["poll_id"])
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        selected_choices = [poll_answer.poll_choice.full() for poll_answer in
                            get_poll_answers(poll, user, cookie)]
        return {
            "result": get_answered_poll(poll, user, selected_choices,
                                        with_article=True),
            "cookie": token.generate_cookie()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
# @http.required_parameters(["private_code"])
@http.require_http_methods("POST")
def read_v2(request, user, cookie):
    """
    @api {post} /polls/read/v2/ Poll read method V2
    @apiName read_v2
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiHeader {String} user_cookie User cookie.
    @apiParam {String} private_code Private code of poll
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            filters = {}

            if request.POST.get('slug'):
                filters['slug'] = request.POST.get('slug')
            else:
                filters['private_code'] = request.POST.get('private_code')
            poll = Poll.objects.get(**filters)
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        selected_choices = [poll_answer.poll_choice.full() for poll_answer in
                            get_poll_answers(poll, user, cookie)]
        return {
            "result": get_answered_poll(poll, user, selected_choices,
                                        with_article=True),
            "cookie": token.generate_cookie()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
@http.require_http_methods("POST")
def feed(request, user, cookie):
    """
    @api {post} /polls/feed/ Poll feed method
    @apiName feed
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiHeader {String} user_cookie User cookie.
    @apiParam {Number} date_begin Date Begin of poll, returns open polls with start time before entered time.
    @apiParam {Number} limit Limit per request.
    @apiParam {Number} short Full = 0, short = 1
    @apiParam {String} own (optional) "true"/"false" If set, then returns own feed.
    @apiParam {String} popularity_period (optional) "day", "week", "month", "year"
    @apiParam {String} answered_status (optional) "answered", "unanswered"
    @apiParam {Number} _poll_type Filters with that poll type.
    @apiParam {String[]} keywords[] list of keywords to filter.
    @apiParam {Number} category_ids[] category id to filter.
    @apiParam {String} popularity (optional) "true"/"false" If set, then returns popular feed.
    @apiParam {Number} page Required if popularity true
    @apiParam {String} finished "true"/"false" Returns finished polls
    @apiParam {String} following "true"/"false" Returns following polls
    @apiParam {Number} user_id ID of another user
    @apiSuccess {Json[]} result Json representation of polls.
    """
    # TODO(temirulan): remove logs
    try:
        user_id = handle_param(request.POST.get("user_id"), int)
        poll_type = handle_param(request.POST.get("_poll_type"), int)
        date_begin = handle_param(request.POST.get("date_begin"), int,
                                  default=Constants.TIMESTAMP_MAX)
        limit = handle_param(request.POST.get('limit'), int,
                             default=Constants.FEED_LIMIT)
        page = handle_param(request.POST.get("page"), int, default=0)
        status = handle_param(request.POST.get('status'), int,
                              list, [Constants.APPROVED, Constants.UNKNOWN])
        popularity = request.POST.get("popularity") == "true"
        popularity_period = request.POST.get("popularity_period")
        finished = request.POST.get("finished") == "true"
        following = request.POST.get("following") == "true"
        answered_status = request.POST.get("answered_status", None)
        own = request.POST.get("own") == "true"
        keywords = request.POST.getlist("keywords[]")
        query = {}
        exclude = {}
        if finished:
            query["date_end__lt"] = get_timestamp_in_milli()
        if following:
            query["user_id__in"] = user.following_user_ids
        if not popularity:
            query["date_begin__lt"] = date_begin
        if popularity:
            if popularity_period == 'day':
                query["date_begin__lte"] = get_timestamp_in_milli() - 86400 * 100
            elif popularity_period == 'week':
                query["date_begin__lte"] = get_timestamp_in_milli() - 7 * 86400 * 100
            elif popularity_period == 'month':
                query["date_begin__lte"] = get_timestamp_in_milli() - 30 * 86400 * 100
            elif popularity_period == 'year':
                query["date_begin__lte"] = get_timestamp_in_milli() - 365 * 86400 * 100
        query["is_active"] = True
        if not own:
            query["status__in"] = status
            query["private_survey"] = False
        if user_id:
            query["user_id"] = user_id
        query["is_template"] = False
        with transaction.atomic():
            if request.POST.getlist("category_ids[]") != [] and request.POST.getlist("category_ids[]") != ['']:
                category_ids = integer_list(request.POST.getlist("category_ids[]"))
            else:
                category_ids = None
            if user and category_ids:
                UserCategory.objects.filter(
                    user=user, category_id__in=category_ids).update(count=0)
            if category_ids:
                query["category_ids__overlap"] = category_ids
                # query["category_id__in"] = category_ids
            if keywords:
                query["keywords_array__overlap"] = keywords
            if own:
                query["user"] = user
                query.pop("user_id", None)
                query.pop("date_end__gt", None)
            if poll_type in [Poll.RATING_SCALE,
                             Poll.SINGLE_CHOICE,
                             Poll.MULTIPLE_CHOICE]:
                query["poll_type"] = poll_type
            if answered_status == 'answered':
                query['answers__user'] = user
            elif answered_status == 'unanswered':
                exclude['answers__user'] = user
            polls = Poll.objects.filter(**query).exclude(**exclude).order_by(
                "-rank" if popularity else "-date_begin")[
                    page * limit if popularity or finished else 0:(
                                                                      page + 1) * limit if popularity or finished
                    else limit]
            answered_polls = []
            for poll in polls:
                selected_choices = [poll_answer.poll_choice.full() for
                                    poll_answer in get_poll_answers(poll, user,
                                                                    cookie)]
                if (int(request.POST.get("short", Constants.FULL))
                        == Constants.SHORT):
                    answered_polls.append(get_answered_poll(poll, user,
                                                            selected_choices,
                                                            is_short=True))
                else:
                    answered_polls.append(get_answered_poll(poll, user,
                                                            selected_choices,
                                                            is_short=False))
        return {
            'result': answered_polls
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


def get_answered_poll(poll, user, selected_choices, is_short=False,
                      with_article=False):
    result = None
    is_admin = False
    if user and user.is_staff:
        is_admin = True
    if is_short:
        result = poll.short(user=user, is_admin=is_admin)
    else:
        result = poll.full(user=user, is_admin=is_admin,
                           with_article=with_article,
                           sel_choice_ids=map(lambda x: x["id"],
                                              selected_choices))
    result['selected_choices'] = selected_choices
    result['is_answered'] = len(selected_choices) > 0
    return result


def get_poll_answers(poll, user, cookie):
    if user is not None:
        return PollAnswer.objects.filter(user=user, poll=poll, is_active=True)
    if cookie is not None:
        return PollAnswer.objects.filter(user_cookie=cookie,
                                         poll=poll,
                                         is_active=True)
    return []


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_cookie_or_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id', 'choice_ids[]'])
def answer_to_poll(request, user, cookie):
    """
    @api {post} /polls/answer_to_poll/ Poll answer method for user answer
    @apiName answer_to_poll
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} poll_id ID of poll.
    @apiParam {Number[]} choice_ids[] List of IDs of chosen choices.
    @apiParam {Number} article_id ID of article.
    @apiParam {String} widget "true"/"false"
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        poll_id = request.POST['poll_id']
        choice_ids = request.POST.getlist('choice_ids[]')
        widget = request.POST.get("widget", "false") == "true"
        article_id = handle_param(request.POST.get('article_id'), int)
        try:
            poll = Poll.objects.get(id=poll_id)
            if poll.date_end < get_timestamp_in_milli():
                return http.code_response(code=codes.POLL_EXPIRED,
                                          message=messages.POLL_EXPIRED)
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        if PollChoice.objects.filter(
                poll=poll, id__in=choice_ids,
                is_active=True).count() != len(choice_ids):
            return http.code_response(code=codes.POLL_CHOICE_NOT_FOUND,
                                      message=messages.POLL_CHOICE_NOT_FOUND)
        if len(choice_ids) == 0:
            return http.code_response(
                code=codes.INVALID_POLL_ANSWER_COUNT,
                message=messages.INVALID_POLL_ANSWER_COUNT)
        if len(choice_ids) > 1 and poll.poll_type != Poll.MULTIPLE_CHOICE:
            return http.code_response(
                code=codes.INVALID_POLL_ANSWER_COUNT,
                message=messages.INVALID_POLL_ANSWER_COUNT)
        if len(set(choice_ids)) != len(choice_ids):
            return http.code_response(
                code=codes.INVALID_POLL_ANSWER_COUNT,
                message=messages.INVALID_POLL_ANSWER_COUNT)
        location_ip = http.get_client_ip(request)
        if user and PollAnswer.objects.filter(poll=poll,
                                              user=user).count() > 0:
            return http.code_response(code=codes.ANSWERED_POLL,
                                      message=messages.ANSWERED_POLL)
        elif not user and cookie and PollAnswer.objects.filter(
                        Q(user_cookie=cookie) | Q(location_ip=location_ip), poll=poll).count() > 0:
            return http.code_response(code=codes.ANSWERED_POLL,
                                      message=messages.ANSWERED_POLL)
        try:
            poll.total_answered_count += len(choice_ids)
            for poll_choice in PollChoice.objects.filter(id__in=choice_ids,
                                                         poll=poll,
                                                         is_active=True):
                poll_choice.answered_count += 1
                poll_choice.save()
                PollAnswer.objects.create(
                    poll=poll,
                    user=user,
                    poll_choice=poll_choice,
                    timestamp=get_timestamp_in_milli(),
                    user_cookie=cookie,
                    location_ip=location_ip)
                UserStat.objects.add_stat(request=request,
                                          user_id=(user.id if user
                                                   else cookie),
                                          poll_id=poll_id,
                                          poll_answered=True,
                                          article_id=article_id,
                                          widget=widget)
            poll.save()
            if user:
                user.increment_answer_count()
        except Exception as e:
            logger.error(str(e))
            return http.code_response(code=codes.WRONG_POLL_CHOICES,
                                      message=messages.WRONG_POLL_CHOICES)
        selected_choices = [poll_choice.full() for poll_choice in
                            PollChoice.objects.filter(is_active=True,
                                                      id__in=choice_ids)]
        return get_answered_poll(poll, user, selected_choices)
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_cookie_or_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id'])
def view_poll(request, user, cookie):
    """
    @api {post} /polls/view_poll/ Poll view method (for statistics)
    @apiName view_poll
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} poll_id ID of poll.
    @apiParam {String} article_id ID of article.
    @apiParam {String} widget "true"/"false"
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = Poll.objects.get(id=request.POST["poll_id"])
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        widget = request.POST.get("widget", "false") == "true"
        UserStat.objects.add_stat(request=request,
                                  user_id=user.id if user else cookie,
                                  poll_id=poll.id,
                                  poll_viewed=True,
                                  widget=widget)
        return http.ok_response()
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
@http.require_http_methods("POST")
def get_random_poll(request, user, cookie):
    """
    @api {post} /polls/get_random_poll/ Retrieves random poll
    @apiName get_random_poll
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token (optional).
    @apiSuccess {Json[]} result Json representation of polls.
    """
    try:
        poll = Poll.objects.random()
        if poll is None:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        selected_choices = [poll_answer.poll_choice.full() for poll_answer
                            in get_poll_answers(poll, user, cookie)]
        return {
            "result": get_answered_poll(poll, user, selected_choices),
            "cookie": token.generate_cookie()
        }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
@http.require_http_methods("POST")
def get_widget_poll(request, user, cookie):
    """
    @api {post} /polls/widget/get/ Retrieves poll for widget
    @apiName get_widget_poll
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token (optional).
    @apiSuccess {Json[]} result Json representation of polls.
    """
    try:
        referer = request.META.get("HTTP_REFERER")
        logger.info("referer: %s" % referer)
        try:
            article = Article.objects.get(article_url=referer)
            poll = article.poll_entry_set.filter(
                is_active=True).order_by('?').first()
            if poll is None:
                raise Exception(messages.ARTICLE_POLL_NONE)
            selected_choices = [poll_answer.poll_choice.full() for poll_answer
                                in get_poll_answers(poll, user, cookie)]
            return {
                "result": get_answered_poll(poll, user, selected_choices)
            }
        except:
            poll = Poll.objects.random()
            if poll is None:
                return http.code_response(code=codes.POLL_NOT_FOUND,
                                          message=messages.POLL_NOT_FOUND)
            selected_choices = [poll_answer.poll_choice.full() for poll_answer
                                in get_poll_answers(poll, user, cookie)]
            return {
                "result": get_answered_poll(poll, user, selected_choices),
                "cookie": token.generate_cookie()
            }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
@http.require_http_methods("POST")
@http.required_parameters(['article_id'])
def get_article_poll(request, user, cookie):
    """
    @api {post} /polls/article/get/ Get article poll
    @apiName get_article_poll
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} article_id ID of article
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            article = Article.objects.get(id=request.POST["article_id"])
        except:
            return http.code_response(code=codes.ARTICLE_NOT_FOUND,
                                      message=messages.ARTICLE_NOT_FOUND)
        poll_entry = article.poll_entry_set.filter(
            is_active=True).select_related("poll").order_by("?").first()

        if poll_entry:
            UserStat.objects.add_stat(request=request,
                                      user_id=user.id if user else cookie,
                                      poll_id=poll_entry.poll.id,
                                      poll_viewed=True,
                                      article_id=article.id,
                                      widget=True)

        if poll_entry is None:
            return http.code_response(code=codes.ARTICLE_POLL_NONE,
                                      message=messages.ARTICLE_POLL_NONE)
        selected_choices = [poll_answer.poll_choice.full() for poll_answer
                            in get_poll_answers(poll_entry.poll, user, cookie)]
        return {
            "result": get_answered_poll(poll_entry.poll,
                                        user, selected_choices),
            "cookie": token.generate_cookie()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@require_http_methods("GET")
def shared_poll(request, private_code):
    """
    Open seasons template
    :timestamp: needed to avoid facebook cache
    """
    template = "front/shared_poll.html"
    params = {}
    try:
        poll = Poll.objects.get(private_code=private_code)
    except:
        raise Http404()
    params["description"] = messages.SHARE_DESCRIPTION_2
    params["poll"] = poll
    return render(request, template, params)


@require_http_methods("GET")
def shared_poll_v2(request, user_id, timestamp):
    """
    DEPRECATED: too long url
    Open seasons template
    :timestamp: needed to avoid facebook cache
    """
    template = "front/shared_poll_v2.html"
    params = {}
    try:
        poll = Poll.objects.get(id=request.GET["poll_id"])
    except:
        raise Http404()
    params["description"] = messages.SHARE_DESCRIPTION_2
    params["user_id"] = user_id
    params["poll"] = poll
    params["timestamp"] = timestamp
    return render(request, template, params)


@require_http_methods("GET")
def shared_poll_v3(request, poll_id):
    """
    DEPRECATED: old version ios support
    Open seasons template
    :timestamp: needed to avoid facebook cache
    """
    template = "front/shared_poll_v3.html"
    params = {}
    try:
        poll = Poll.objects.get(id=poll_id)
    except:
        raise Http404()
    params["description"] = messages.SHARE_DESCRIPTION_2
    params["poll"] = poll
    return render(request, template, params)


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
@http.require_http_methods("POST")
@http.required_parameters(["poll_id"])
def repost(request, user, cookie):
    """
    @api {post} /polls/repost/ Repost poll
    @apiName respost
    @apiGroup Polls
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} poll_id ID of poll
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = Poll.objects.get(id=request.POST["poll_id"])
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
            poll.user.increment_repost_count()
        return http.ok_response()
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id', 'comment'])
def create_comment(request, user):
    """
        @api {post} /polls/create_comment/ Poll read method
        @apiName get_comment
        @apiGroup Polls
        @apiHeader {String} Csrf-Token CSRF token.
        @apiHeader {String} Auth-Token Authentication token.
        @apiParam {String} poll_id id of poll.
        @apiSuccess {Json} result Json representation of poll.
        """
    try:
        try:
            comment = request.POST["comment"]
            poll_id = request.POST["poll_id"]

            PollComment.objects.create(
                comment=comment,
                poll=Poll.objects.get(id=poll_id),
                user=user
            )

            poll_comment = PollComment.objects.last()

        except:
            return HttpResponse(status=400)

        return {
            "result": {
                "status_code": 200,
                "comment_id": str(poll_comment.id),
                "comment": u"{}".format(comment).encode('utf-8'),
                "poll_id": poll_id,
                "created_date": u"{}".format(timezone.now()).encode('utf-8'),
                "user": {
                    "username": u"{}".format(user.username).encode('utf-8'),
                    "full_name": u"{}".format(user.full_name).encode('utf-8'),
                    "avatar": u"{}".format(get_cdn_url(user.avatar)).encode('utf-8')
                }

            },

        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(['comment_id'])
def delete_comment(request):
    """
        @api {post} /polls/delete_comment/ comment delete by id method
        @apiName delete_comment
        @apiGroup Polls
        @apiHeader {String} Csrf-Token CSRF token.
        @apiHeader {String} Auth-Token Authentication token.
        @apiParam {String} poll_id id of poll.
        @apiSuccess {Json} result Json representation of poll.
        """
    try:
        try:
            comment = PollComment.objects.get(id=request.POST["comment_id"])
            comment.delete()
            return {
                "result": True
            }
        except:
            return http.code_response(code="Not Found",
                                      message="Not Found")

    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id'])
def get_comment(request):
    """
        @api {post} /polls/get_comment/ Poll read method
        @apiName get_comment
        @apiGroup Polls                                                                                         
        @apiHeader {String} Csrf-Token CSRF token.
        @apiHeader {String} Auth-Token Authentication token.
        @apiParam {String} poll_id id of poll.
        @apiSuccess {Json} result Json representation of poll.
        """
    try:
        try:
            comments = PollComment.objects.filter(poll_id=request.POST["poll_id"])
        except:
            return http.code_response(code="Not Found",
                                      message="Not Found")

        return {
            "result": {
                "comments": [{
                    "id": u"{}".format(i.id).encode("utf-8"),
                    "comment": u"{}".format(i.comment).encode('utf-8'),
                    "user": {
                        "username": u"{}".format(i.user.username).encode('utf-8'),
                        "full_name": u"{}".format(i.user.full_name).encode('utf-8'),
                        "avatar": (u"{}".format(get_cdn_url(i.user.avatar)).encode('utf-8')) if i.user.avatar else (
                            u"{}".format(
                                "data:image/png;base64,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"))

                    },
                    "created_date": u"{}".format(i.timestamp).encode('utf-8'),
                } for i in comments],

                "cookie": token.generate_cookie()
            }
        }

    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
def get_polls_votes_count(request, user):
    try:
        try:
            polls = Poll.objects.filter(user=user)
            sum = 0
            for i in polls:
                sum = sum + i.total_answered_count
            return {
                "result": {
                    "count": int(sum)
                }
            }

        except Exception as exc:
            logger.error(exc)
            return http.code_response(codes.SERVER_ERROR, message=str(exc))

    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
# @http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(['user_id'])
def get_user_info_and_polls(request):
    try:
        try:
            user = MainUser.objects.get(id=request.POST['user_id'])
            polls = Poll.objects.filter(user=user)

            return {
                "result": {
                    "user": {
                        "full_name": u"{}".format(user.full_name).encode("utf-8"),
                        "username": u"{}".format(user.username),
                        "avatar": (u"{}".format(get_cdn_url(user.avatar)).encode('utf-8')) if user.avatar else (
                            u"{}".format(
                                "data:image/png;base64,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"))

                    },

                    "polls": [i.full() for i in polls]
                }
            }

        except Exception as exc:
            logger.error(exc)
            return http.code_response(codes.SERVER_ERROR, message=str(exc))

    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))
