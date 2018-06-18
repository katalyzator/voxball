#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, datetime
import sys
import uuid
import time
import json, sys
import urllib2
from pprint import pprint

import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votem.settings")
django.setup()

from polls.models import Poll
from pushtoken.models import PushSender


def get_push_tokens():
    push_web = []
    push_ios = []
    for line in open("/logs/push_info.logs", "r"):
        line = line.replace("\n", "")
        s = line.split("=", 1)[1]
        s = s.split("-", 2)
        if s[1] == 'ios':
            if s[2] not in push_ios:
                push_ios.append(s[2])
        else:
            if push_web not in push_web:
                push_web.append(s[2])
    return push_web, push_ios


def get_poll(key):
    # polls = Poll.objects.filter(private_code=key).all()
    polls = Poll.objects.filter(id=key).all()
    if polls:
        return polls[0]
    return None


def send_push_web(data, tokens):
    if not len(tokens):
        return
    push_data = {
        "notification": {
            "title": data['title'],
            "body": data['body'],
            "click_action": data['click_action'],
            # "icon": "https://test.devz.voxball.io/static/media/box.jpg",
        },
        "registration_ids": tokens
    }
    send_push(push_data)


def send_push_ios(data, tokens):
    if not len(tokens):
        return
    push_data = {
        "notification": {
            "title": data['title'],
            "body": data['body'],
            "click_action": data['click_action'],
            "sound": "default",
            "icon": "https://voxball.com/media/box.jpg",
        },
        "content_available": True,
        "priority": "high",
        "registration_ids": tokens
    }
    send_push(push_data)


def send_push(push_data):
    req = urllib2.Request('https://fcm.googleapis.com/fcm/send')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization',
                   'key=AAAAtU2nZFI:APA91bGvJXxR9PZpmhQGzrdMU3IfKloL4IT9n1yVz1srYhPm-B34_Zuznj8_-NNFSaqT1u9ihs1_BmIFWlirOHvmFRsruWOtFLMCNdf6ITs63FGeMxOhMM5YSjSZXTpZJXQNVSXvx9aa')
    response = urllib2.urlopen(req, json.dumps(push_data))
    print response


if __name__ == "__main__":
    while True:
        for el in PushSender.objects.filter(sent=False).all():
            push_web, push_ios = get_push_tokens()
            # private_key = el.url.split("/")[-1]
            # poll = get_poll(private_key)
            poll_id = el.url.split("-")[-1]
            poll = get_poll(poll_id)
            if poll:
                send_push_web({
                    'title': u"Интересные опросы на Voxball.com",
                    'body': el.title,
                    'click_action': el.url
                }, push_web)
                send_push_ios({
                    'title': u"Интересные опросы на Voxball.com",
                    'body': el.title,
                    'click_action': poll.private_code
                }, push_ios)
            el.sent = True
            el.save()
        time.sleep(5)
