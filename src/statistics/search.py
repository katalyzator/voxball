from django.apps import apps
from django.conf import settings
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Integer, Boolean, Keyword, \
    Long
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

connections.create_connection(hosts=[settings.ELASTICSEARCH_URL])


class UserStatIndex(DocType):
    poll = Long()
    article = Long()
    user = Keyword()
    agent = Long()
    referer = Text()
    location = Text()
    city = Keyword()
    region = Keyword()
    country = Keyword()
    timestamp = Long()
    poll_viewed = Boolean()
    poll_created = Boolean()
    poll_answered = Boolean()
    user_created = Boolean()
    widget = Boolean()
    date_added = Date()

    class Meta:
        index = 'userstat'


def bulk_indexing():
    UserStat = apps.get_model('statistics', 'UserStat')
    UserStatIndex.init()
    es = Elasticsearch([settings.ELASTICSEARCH_URL])
    bulk(client=es, actions=(b.indexing() for b in UserStat.objects.all().iterator()))
