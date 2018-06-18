from django.contrib.auth import get_user_model
from django.db.models import F
from models import Poll
from utils import image_utils, messages
from utils.Constants import MINUTES, SECONDS
from utils.poll_utils import rank_poll
from utils.time_utils import get_timestamp_in_milli
import celery
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@celery.task(default_retry_delay=10 * SECONDS, max_retries=10)
def set_texted_image(poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
        if poll.image:
            poll.facebook_image = image_utils.get_texted_image(poll.image,
                                                               poll.title)
            poll.save()
    except Exception as e:
        logger.error(str(e))
        raise set_texted_image.retry(e)


@celery.task(default_retry_delay=10 * SECONDS, max_retries=10)
def update_category_counters(poll_id, category_ids):
    try:
        from polls.models import Poll, UserCategory
        try:
            poll = Poll.objects.get(id=poll_id)
        except:
            raise Exception(messages.POLL_NOT_FOUND)
        if poll.is_active:
            UserCategory.objects.filter(
                category_id__in=category_ids).update(count=F('count') + 1)
    except Exception as e:
        logger.error(str(e))
        raise update_category_counters.retry(e)


@celery.task(default_retry_delay=10 * MINUTES, max_retries=10)
def rank_polls():
    try:
        polls = Poll.objects.all()
        for poll in polls:
            poll.rank = rank_poll(poll)
            poll.save()
    except Exception as e:
        logger.error(str(e))
        raise rank_polls.retry(e)


@celery.task(default_retry_delay=10 * MINUTES, max_retries=10)
def check_expired_polls():
    try:
        date_end = get_timestamp_in_milli()
        polls = Poll.objects.filter(date_end__lt=date_end, is_active=True)
        polls.update(is_active=False)
    except Exception as e:
        logger.error(str(e))
        raise check_expired_polls.retry(e)
