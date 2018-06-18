from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q, aggs
import json
import operator


def search_by_date(time_begin, time_end, article_id=None, agent=None,
                   country=None, city=None, poll_id=None, widget=False):
    try:
        client = Elasticsearch([settings.ELASTICSEARCH_URL])
        s = Search(using=client, index="userstat")

        query_list = []
        query_list.append(Q('range', timestamp={'gte': time_begin,
                                                'lt': time_end}))
        if agent is not None:
            query_list.append(Q('match', agent=agent))
        if country:
            query_list.append(Q('match', country=country))
        if city:
            query_list.append(Q('match', city=city))
        if poll_id:
            query_list.append(Q('match', poll=poll_id))
        if article_id:
            query_list.append(Q('match', article=article_id))
        if widget:
            query_list.append(Q('match', widget=widget))

        query = reduce(operator.and_, query_list)

        poll_created_filter = Q('match', poll_created=True)
        poll_viewed_filter = Q('match', poll_viewed=True)
        poll_answered_filter = Q('match', poll_answered=True)
        user_created_filter = Q('match', user_created=True)

        poll_count = s.query((query & Q('bool', filter=[poll_created_filter]))).count()
        view_count = s.query((query & Q('bool', filter=[poll_viewed_filter]))).count()
        user_count = s.query((query & Q('bool', filter=[user_created_filter]))).count()
        
        s = s.query((query & Q('bool', filter=[poll_answered_filter])))
        answer_count = s.count()
        a = A('cardinality', field='user')
        s.aggs.bucket('unique_users', a)
        s = s.execute()

        return {'poll_count': poll_count,
                'view_count': view_count,
                'answer_count': answer_count,
                'user_count': user_count,
                'respondents_count': s.aggregations.unique_users['value']}
    except:
        return None
