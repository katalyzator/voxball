# -*- coding: utf-8 -*-
"""
Django settings for votem project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'if2m32ko8$l21wa+xv9bgj*2n$+g*%*uyd%-h05=m#0wj7s#g1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'authe',
    'polls',
    'moderators',
    'statistics',
    # 'pushtoken',
    'django_celery_beat',
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'votem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'votem.context_processors.site_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'votem.wsgi.application'

DATABASES = {
    'default': {
        'NAME': os.environ.get('PRIMARY_DB_NAME', 'votem'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': os.environ.get('PRIMARY_DB_USER', 'admin'),
        'PASSWORD': os.environ.get('PRIMARY_DB_PASS', '12345'),
        'HOST': os.environ.get('PRIMARY_DB_HOST', '127.0.0.1'),
        'PORT': "",
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'authe.MainUser'
STATISTICS_MODEL = 'statistics.UserStat'
CITY_MODEL = 'authe.City'
POLL_MODEL = 'polls.Poll'
CATEGORY_MODEL = 'polls.Category'
ACTIVATION_KEY_LENGTH = 20
PASSWORD_LENGTH = 6
SITE_URL = 'http://localhost:8000'

COOKIE_LENGTH = 50

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)


BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'django-db'
CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

JWT_KEY = 'votem-secret-key0286'
JWT_ALGORITHM = 'HS256'

AUTH_TOKEN_HEADER_NAME = ["AUTH_TOKEN", "HTTP_AUTH_TOKEN", "Auth-Token"]
AUTH_TOKEN_COOKIE_NAME = "auth-token"
AUTH_TOKEN_POST_NAME = "Auth-Token"

USER_COOKIE_NAME = "user_cookie"
USER_COOKIE_HEADER_NAME = "HTTP_USER_COOKIE"

FACEBOOK_PROFILE = 'https://www.facebook.com/profile.php?id={0}'
FACEBOOK_INFO_URL = "https://graph.facebook.com/v2.8/me?access_token={0}&fields=id,name,email&format=json"
FACEBOOK_AVATAR_URL = "https://graph.facebook.com/{0}/picture?type=large"

EMAIL_HOST = 'mail.privateemail.com'
EMAIL_HOST_USER = 'robot@voxball.com'
EMAIL_HOST_PASSWORD = 'fkM#G74ns'
FROM_EMAIL = u'Voxball Team <robot@voxball.com>'
#EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
#EMAIL_HOST_USER = 'AKIAIRJAMX7BLPUH3OKA'
#EMAIL_HOST_PASSWORD = 'AoOJDOxMrTI2vrC+mrDvnvffEbxyhEXjKVuy40wGYirK'
#FROM_EMAIL = u'Voxball Team <voxballcompany@gmail.com>'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

#EMAIL = "voxballcompany@gmail.com"
#EMAIL_PASS = "VoxPass123"

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = '/media/'
if os.environ.get('DEV', '0') == '0':
    MEDIA_URL = 'https://voxball.com/media/'
else:
    MEDIA_URL = 'https://test.devz.voxball.io/media/'
#Amazon S3 settings
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#AWS_ACCESS_KEY_ID = "AKIAJBCEA7C7VRNTFHDA"
#AWS_SECRET_ACCESS_KEY = "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"
#AWS_STORAGE_BUCKET_NAME = "voxball"
#AWS_DEFAULT_ACL = "public-read"
#AWS_S3_FILE_OVERWRITE = False
#AWS_QUERYSTRING_AUTH = False
#BUCKET_URL = "https://voxball.s3.amazonaws.com/"

#AWS_CDN_URL = "https://d1ssi13ekayzc9.cloudfront.net/"


ADMINS = (
)

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s path: %(pathname)s module: %(module)s method: %(funcName)s  row: %(lineno)d message: %(message)s'
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
#     },
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'utils.handlers.MainAdminEmailHandler',
#             'formatter': 'verbose',
#         },
#         'authe_log_file': {
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': '/logs/authe.log',
#             'maxBytes': 1024*1024*15, # 15MB
#             'backupCount': 10,
#             'formatter': 'verbose'
#         },
#         'polls_log_file': {
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': '/logs/polls.log',
#             'maxBytes': 1024*1024*15, # 15MB
#             'backupCount': 10,
#             'formatter': 'verbose'
#         },
#         'utils_log_file': {
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': '/logs/utils.log',
#             'maxBytes': 1024*1024*15, # 15MB
#             'backupCount': 10,
#             'formatter': 'verbose'
#         },
#         'moderators_log_file': {
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': '/logs/moderators.log',
#             'maxBytes': 1024*1024*15, # 15MB
#             'backupCount': 10,
#             'formatter': 'verbose'
#         },
#         'console': {
#             'level': 'INFO',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         'authe': {
#             'handlers': ['authe_log_file', 'mail_admins'],
#             'level': 'INFO',
#         },
#         'polls': {
#             'handlers': ['polls_log_file', 'mail_admins'],
#             'level': 'INFO',
#         },
#         'utils': {
#             'handlers': ['utils_log_file', 'mail_admins'],
#             'level': 'INFO',
#         },
#         'moderators': {
#             'handlers': ['moderators_log_file', 'mail_admins'],
#             'level': 'INFO',
#         },
#     }
# }

APPEND_SLASH = True
FRONT_URL = "https://voxball.com"
FRONT_404 = FRONT_URL + "/404"
FRONT_AUTH_URL = FRONT_URL + "/login"
POLL_URL = FRONT_URL + "/poll/{id}"
POLL_URL_V2 = FRONT_URL + "/api/polls/front/poll/shared/?poll_id={id}"
PASSWORD_RESET_URL = FRONT_URL + "/reset/{token}"
EMAIL_ACTIVATION_URL = FRONT_URL + "/authe/account_activate/{token}"

FB_LIKES_URL = "http://graph.facebook.com/?fields=og_object%7Blikes.summary(true).limit(0)%7D,share&id={0}"
FB_SHARES_URL = "http://graph.facebook.com/?fields=share&id={}"

SMS_MOBIZON_KEY = "c3139e4a56ff997f9a624322d3325ae6ae626a54"
SMS_SEND_URL = "https://api.mobizon.com/service/message/sendsmsmessage"
SMS_ACTIVATION_TEXT = u"Voxball код: {password}"

# minutes
ACTIVATION_TIME = 10
POLL_IMG_SIZE = (715, 400)
POLL_AVATAR_SIZE = (144, 144)

IPINFO_URL = 'http://ipinfo.io/{0}/json'

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "localhost:9200")

DEFAULT_POLL_IMAGE_URL = "files/photos/photo_10.jpg"
DEFAULT_LAST_ID = 9999999999
DEFAULT_LIMIT = 10

PATH_TO_COUNTRY_CODE_MAPPING = os.path.join(BASE_DIR,
                                            "files/country_code_mapping.json")

POLL_TITLE_COUNT = 10

FAVICON_URL = "https://www.google.com/s2/favicons?domain={url}"

CSRF_ON = False
CSRF_TOKEN_HEADER_NAME = 'HTTP_CSRF_TOKEN'
CSRF_TIMESTAMP_LENGTH = 13
CSRF_MD5_HASH_LENGTH = 32

CSRF_MOBILE = 'm'
CSRF_WEB = 'w'

CSRF_WEB_KEY = 'jessicalba'
CSRF_MOBILE_KEY = 'AEGON_TARGARYEN'

CSRF_TIME_LIMIT = 120000

ONE_SIGNAL_APP_ID = 'd6471961-d8ac-4b49-9543-e5a34e191636'
ONE_SIGNAL_HEADER = 'Y2ZmMDVjYzYtMDA0MC00Njg0LWI3MjktMGRiODVhOGQwMGEx'
