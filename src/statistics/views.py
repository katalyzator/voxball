# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from utils import codes, messages, http
from utils.facebook import get_likes_info
from utils.search_utils import search_by_date


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("POST")
@http.required_parameters(['time_begin', 'time_end'])
def search(request):
    """
    @api {post} /statistics/search/ Search method
    @apiName search
    @apiGroup statistics
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token
    @apiParam {Number} time_begin unix timestamp in millisecs (required)
    @apiParam {Number} time_end  unix timestamp in millisecs (required)
    @apiParam {Number} agent WEB = 0 IOS = 1 ANDROID = 2 (optional)
    @apiParam {Number} poll_id statistics of single poll (optional)
    @apiParam {Number} article_id ID of article
    @apiParam {String} country Country filter (optional)
    @apiParam {String} city City filter (optional)
    @apiParam {String} widget "true"/"false"
    @apiParam {String} with_fb "true"/"false"
    @apiSuccess {json} result Statistics of polls
    """
    try:
        try:
            time_begin = int(request.POST['time_begin'])
            time_end = int(request.POST['time_end'])
            agent = request.POST.get('agent')
            country = request.POST.get('country')
            city = request.POST.get('city')
            poll_id = request.POST.get('poll_id')
            article_id = request.POST.get('article_id')
            widget = request.POST.get("widget", "false") == "true"
            with_fb = request.POST.get("with_fb", "false") == "true"
        except Exception as exc:
            return http.code_response(code=codes.MISSING_REQUIRED_PARAMS,
                                      message=messages.MISSING_REQUIRED_PARAMS)
        result = search_by_date(time_begin=time_begin,
                                time_end=time_end,
                                agent=int(agent) if agent else None,
                                country=country,
                                city=city,
                                poll_id=poll_id,
                                article_id=article_id,
                                widget=widget)
        if with_fb:
            result["fb_info"] = get_likes_info(
                settings.POLL_URL_V2.format(id=request.POST["poll_id"]))
        return {
            'result': result
        }
    except Exception as exc:
        return http.code_response(codes.SERVER_ERROR, message=str(exc))

