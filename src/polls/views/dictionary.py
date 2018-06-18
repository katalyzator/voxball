# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from moderators.models import PollTemplate
from polls.models import Category, Keyword
from utils import codes, http
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@http.json_response()
@http.require_http_methods("GET")
def get_all_categories(request):
    """
    @api {get} /polls/get_all_categories/ Get all categories with subcategories
    @apiName get_all_categories
    @apiGroup Polls
    @apiSuccess {Json} result Json representation of all categories.
    """
    try:
        return {
            'categories': [category.full() for category in
                           Category.objects.filter(is_active=True,
                                                   parent=None)]
        }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.require_http_methods("GET")
def get_all_poll_templates(request):
    """
    @api {get} /polls/get_all_poll_templates/ Get all poll templates.
    @apiName get_all_poll_templates
    @apiGroup Polls
    @apiSuccess {Json} result Json representation of all poll templates.
    """
    try:
        return {
            'templates': [template.full() for template in
                          PollTemplate.objects.filter(is_active=True)]
        }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.require_http_methods("GET")
def get_all_keywords(request):
    """
    @api {get} /polls/get_all_keywords/ Get all keywords method.
    @apiName get_all_keywords
    @apiGroup Polls
    @apiParam {Number} category_id ID of category
    @apiSuccess {Json} result Json representation of all keywords.
    """
    try:
        query = {"is_active": True}
        if request.POST.getlist("category_ids[]"):
            query["category_id__in"] = request.POST.getlist("category_ids[]")
        return {
            'keywords': [keyword.full() for keyword in
                         Keyword.objects.filter(**query).order_by("-rank")]
        }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))
