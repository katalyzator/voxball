# -*- coding: utf-8 -*-
from django.conf import settings
import logging
import requests
import json


logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location(ip):
    location = {'country': '', 'city': '', 'region': ''}
    try:
        url = settings.IPINFO_URL.format(ip)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return location
    except Exception as e:
        logger.error(str(e))
    return location
