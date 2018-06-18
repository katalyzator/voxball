# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger
from django.core.mail import EmailMessage
from django.conf import settings
from utils.Constants import MINUTES
from utils.email_utils import valid_email
from utils.string_utils import valid_uuid4
import celery
import json
import requests
import urllib2
import urllib

logger = get_task_logger(__name__)


@celery.task(default_retry_delay=2 * MINUTES, max_retries=2)
def email(to, subject, message):
    """
    Sends email to user/users. 'to' parameter must be a string or list.
    """
    # Converto to list if one user's email is passed
    from authe.models import BlackList
    if isinstance(to, basestring):  # Python 2.x only
        to = [to]
    # Check if email is not in BlackList
    black_list = [x.email for x in BlackList.objects.filter(email__in=to)]
    for e in black_list:
        to.remove(e)
    try:
        email_list = list(filter(lambda email: valid_email(email), to))
        msg = EmailMessage(subject, message, from_email=settings.FROM_EMAIL,
                           to=email_list)
        msg.content_subtype = "html"
        msg.send()
    except Exception as exc:
        logger.error((u'''Failed to send email,
            to={0}, subject={1}, message={2}, with exception={3}''').format(
            to, subject, message, str(exc)))
        raise email.retry(exc=exc)


# retry in 2 minutes
@celery.task(default_retry_delay=2 * MINUTES, max_retries=2)
def send_message(number, text):
    """
    Module for sending sms.
    """
    text = text.encode('utf-8')
    try:
        values = {
            'apiKey': settings.SMS_MOBIZON_KEY,
            'recipient': number,
            'text': text,
            'output': 'json',
            'api': 'v1'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = urllib.urlencode(values)
        req = urllib2.Request(settings.SMS_SEND_URL, data, headers)
        resp = urllib2.urlopen(req, timeout=60)
        return resp.read()
    except Exception as exc:
        raise send_message.retry(exc=exc)
