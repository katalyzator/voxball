# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from authe.models import BlackList
import json
import urllib2


@csrf_exempt
def handle_bounces(request):
    """
        View for handling bounces
        Adds email to BlackList with is_bounced = True
    """
    #  needed for confirmation of subscription
    if request.META['HTTP_X_AMZ_SNS_MESSAGE_TYPE'] == 'SubscriptionConfirmation':
        message_body = json.loads(request.body)
        url = message_body['SubscribeURL']
        _ = urllib2.urlopen(url)
        return HttpResponse()
    elif request.META['HTTP_X_AMZ_SNS_MESSAGE_TYPE'] == 'Notification':
        message_body = json.loads(request.body)
        message = json.loads(message_body['Message'])
        bounce = message['bounce']
        msg_to_send = ""
        for recipient in bounce['bouncedRecipients']:
            email = recipient['emailAddress']
            msg_to_send += email + " "
            black_email, _ = BlackList.objects.get_or_create(email=email)
            black_email.is_bounced = True
            black_email.save()
    # response code should be 2xx - 400
    return HttpResponse()


@csrf_exempt
def handle_complaints(request):
    """
        View for handling complaints
        Adds email to BlackList with is_complained = True
    """
    #  needed for confirmation of subscription
    if request.META['HTTP_X_AMZ_SNS_MESSAGE_TYPE'] == 'SubscriptionConfirmation':
        message_body = json.loads(request.body)
        url = message_body['SubscribeURL']
        _ = urllib2.urlopen(url)
        return HttpResponse()
    elif request.META['HTTP_X_AMZ_SNS_MESSAGE_TYPE'] == 'Notification':
        message_body = json.loads(request.body)
        message = json.loads(message_body['Message'])
        complaint = message['complaint']
        msg_to_send = ""
        for recipient in complaint['complainedRecipients']:
            email = recipient['emailAddress']
            msg_to_send += email + " "
            black_email, _ = BlackList.objects.get_or_create(email=email)
            black_email.is_complained = True
            black_email.save()
    # response code should be 2xx - 400
    return HttpResponse()
