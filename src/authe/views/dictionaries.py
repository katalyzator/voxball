# -*- coding: utf-8 -*-
from authe.models import Country, City, AppVersion
from django.views.decorators.csrf import csrf_exempt
from utils import codes, http
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@http.json_response()
@http.require_http_methods("GET")
def countries(request):
    """
    @api {get} /authe/countries/ Get all countries
    @apiName countries
    @apiGroup Authe
    @apiSuccess {Json} result Json representation of all categories.
    """
    try:
        return {
            'result': [c.full() for c in Country.objects.filter(is_active=True)]
        }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.require_http_methods("GET")
def cities(request, country_id):
    """
    @api {get} /authe/cities/:country_id/ Get all cities by country_id
    @apiName get_cities_by_country_id
    @apiGroup Authe
    @apiSuccess {Json} result Json representation of cities of countries.
    """
    try:
        return {
            'result': [c.short() for c in City.objects.filter(country_id=country_id)]
        }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.require_http_methods("GET")
def app_version(request):
    """
    @api {get} /authe/app/version/ Get app version
    @apiName app_version
    @apiGroup Authe
    @apiSuccess {Json} result Json
    """
    try:
        app_version = AppVersion.objects.first()
        return {
            "result": app_version.full() if app_version else None
        }
    except Exception as e:
        logger.error(str(e))
        return http.code_response(codes.SERVER_ERROR, message=str(e))
