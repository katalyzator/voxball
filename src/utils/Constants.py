# -*- coding: utf-8 -*-
SIMPLE = 0
FACEBOOK = 1

SOCIAL_TYPES = (
    (SIMPLE, u"simple login"),
    (FACEBOOK, u"facebook")
    )

WEB = 0
IOS = 1
ANDROID = 2

DEVICES = (
    (WEB, u"Браузер"),
    (IOS, u"iOS"),
    (ANDROID, u"Андроид"),
    )

SINGLE_CHOICE_MIN_COUNT = 2
TIMESTAMP_MAX = 9999999999999
FEED_LIMIT = 10
SECONDS = 1
MINUTES = 60 * SECONDS

POLL_NUMBER = 10
RATING_SCALE_COUNT = 5

FULL = 0
SHORT = 1

REJECTED = 0
UNKNOWN = 1
APPROVED = 2

STATUS_TYPES = (
    (APPROVED, u"approved"),
    (UNKNOWN, u"unknown"),
    (REJECTED, u"rejected"),
    )

DAY = 24 * 3600 * 1000
YEAR = DAY * 365

EMAIL_REGISTER = 0
TELEPHONE_REGISTER = 1
FACEBOOK_REGISTER = 2
UNDEFINED = 3

USER_TYPES = (
    (EMAIL_REGISTER, u"email register"),
    (TELEPHONE_REGISTER, u"telephone register"),
    (FACEBOOK_REGISTER, u"facebook register"),
    (UNDEFINED, u"undefined")
    )

PUBLIC = 0
PRIVATE = 1

PRIVACY_TYPES = (
    (PUBLIC, u"Public"),
    (PRIVATE, u"Private"),
)

DELIMITER = ' '

DUMMY = 0
POLL_CREATED = 1
POLL_ANSWERED = 2
POLL_EXPIRED = 3

POLL_URL = "https://voxball.com/poll/{0}"

PUSH_TYPES = (
    (DUMMY, u"Dummy push"),
    (POLL_CREATED, u"Опрос создан"),
    (POLL_ANSWERED, u"Опрос отвечен"),
    (POLL_EXPIRED, u"Опрос закончен"),
    )

POLL_CODE_MAX_RETRIES = 10
