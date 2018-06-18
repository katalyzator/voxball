# -*- coding: utf-8 -*-
from authe.models import Country, City
from django.conf import settings
from polls.models import Poll
from utils.agent_utils import get_agent
from utils.Constants import SECONDS
from utils.location_utils import get_location
from utils.time_utils import get_timestamp_in_milli
import celery
import json
import logging

logger = logging.getLogger(__name__)


@celery.task(default_retry_delay=10 * SECONDS, max_retries=2)
def add_to_statistics(agent, location, referer, user="", poll_id=None,
                      poll_created=False, poll_answered=False,
                      poll_viewed=False, user_created=False, article_id=None,
                      widget=False):
    try:
        from models import UserStat
        from moderators.models import Article
        agent = get_agent(agent)
        poll = None
        article = None
        if poll_id:
            poll = Poll.objects.filter(id=poll_id).first()
        logger.info("article: %s" % article)
        if article_id:
            try:
                article = Article.objects.get(id=article_id)
            except Exception as e:
                logger.error(str(e))
        loc = get_location(location)
        country_code = loc.get('country', '')
        city = loc.get('city', '')
        region = loc.get('region', '')
        city_obj = None
        country = None
        if country_code:
            country_code_mapping = json.loads(open(
                settings.PATH_TO_COUNTRY_CODE_MAPPING).read())
            country_name = country_code_mapping.get(country_code, '')
            try:
                country, _ = Country.objects.get_or_create(name=country_name,
                                                           code=country_code)
            except Exception as e:
                logger.error(e)
            if city:
                try:
                    city_obj, _ = City.objects.get_or_create(name=city,
                                                             country=country)
                except Exception as e:
                    logger.info(u"city: %s country: %s" % (
                        city, country))
                    logger.error(e)
        UserStat.objects.create(poll=poll,
                                article=article,
                                user=str(user),
                                poll_viewed=poll_viewed,
                                poll_created=poll_created,
                                poll_answered=poll_answered,
                                user_created=user_created,
                                agent=agent,
                                referer=referer,
                                location=location,
                                country=(str(country.id) if country
                                         else country_code),
                                city=str(city_obj.id) if city_obj else city,
                                region=region,
                                timestamp=get_timestamp_in_milli(),
                                widget=widget)
    except Exception as e:
        logger.error(e)
        raise add_to_statistics.retry(exc=e)
