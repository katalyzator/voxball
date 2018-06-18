# -*- coding: utf-8 -*-
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_likes_info(_id):
    """
    _id should be link to poll
    :Likes always 0, => retrieve only shares
    """
    try:
        resp = requests.get(settings.FB_SHARES_URL.format(_id))
        if resp.status_code == 200:
            response = resp.json()
            share_count = response["share"]["share_count"]
            comment_count = response["share"]["comment_count"]
            try:
                like_count = response["og_object"]["likes"]["summary"]["total_count"]
            except:
                like_count = 0
            return {
                "share_count": share_count,
                "comment_count": comment_count,
                "like_count": like_count
            }
        return {"share_count": 0,
                "comment_count": 0,
                "like_count": 0}
    except Exception as exc:
        logger.error(exc)
        return {"share_count": 0,
                "comment_count": 0,
                "like_count": 0}
