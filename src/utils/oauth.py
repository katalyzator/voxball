import json
import logging
import urllib
import urllib2
from urlparse import urlparse

from django.conf import settings

STATUS_OK = '200'
logger = logging.getLogger(__name__)


def get_facebook_info(access_token):
    try:
        request_url = settings.FACEBOOK_INFO_URL.format(access_token)
        response = urllib2.urlopen(request_url).read()
        return json.loads(response)
    except Exception as e:
        logger.error(e)
        return None


def get_redirected_url(url):
    try:
        request = urllib2.Request(url)
        result = urllib2.urlopen(request)
        resulting_url = result.geturl()
        return resulting_url
    except Exception as e:
        logger.error(e)
        return None


def get_facebook_avatar(fb_id):
    fb_avatar_url = get_redirected_url(settings.FACEBOOK_AVATAR_URL.format(fb_id))
    fb_avatar_name = None
    fb_avatar_content = None
    try:
        fb_avatar_name = urlparse(fb_avatar_url).path.split('/')[-1]
        fb_avatar_content = urllib.urlretrieve(fb_avatar_url)
    except Exception as e:
        print str(e)
        pass
    return fb_avatar_name, fb_avatar_content
