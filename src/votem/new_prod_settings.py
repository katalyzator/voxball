import os
from settings import *

SITE_URL = 'https://voxball.com'
ALLOWED_HOSTS = ["voxball.ru", "voxball.kz", "voxball.com", "voxball.io"]

if os.environ.get('DEV', '0') == '1':
    SITE_URL = 'https://test.devz.voxball.io'
    ALLOWED_HOSTS = ["test.devz.voxball.io"]

DEBUG = False

BROKER_URL = 'amqp://votem:votem@rabbit:5672/votem'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


STATIC_URL = '/back_static/'
STATIC_ROOT = "/static"

# MEDIA_ROOT = "/media"

# ADMINS_LIST = ['aiba.prenov@gmail.com']

# ADMINS = (
#     ('Aibek Prenov', 'aiba.prenov@gmail.com'),
# )
ADMINS_LIST = []

ADMINS = tuple()

CSRF_ON = True
