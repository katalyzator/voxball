from models import UserStat
from polls.models import Poll
from utils.agent_utils import get_agent
from utils.Constants import MINUTES, SECONDS
from utils.location_utils import get_location
from utils.time_utils import get_timestamp_in_milli
from random import *
import random

def test_add_to_statistics():
    agent_list = [0,1,2]
    agent = random.choice(agent_list)
    referer_list = ["google","yandex","vk","facebook"]
    referer = random.choice(referer_list)
    poll_id = randint(1, 500)
    poll = Poll.objects.get(id=poll_id)
    user = randint(1, 79)
    location = ".".join(map(str, (random.randint(0, 255) 
                        for _ in range(4))))
    if location:
        loc = get_location(location)
        country = loc['country']
        city = loc['city']
        region = loc['region']
    time = get_timestamp_in_milli()
    poll_viewed=False
    poll_created=False 
    poll_answered=False
    user_created=False
    action = randint(0, 3)
    if action == 0:
        poll_viewed = True
    if action == 1:
        poll_created = True
    if action == 2:
        poll_answered = True
    if action == 3:
        user_created = True
    UserStat.objects.create(poll=poll,
                            user=user,
                            poll_viewed=poll_viewed,
                            poll_created=poll_created,
                            poll_answered=poll_answered,
                            user_created=user_created,
                            agent=agent,
                            referer=referer,
                            location=location,
                            country=country,
                            city=city,
                            region=region,
                            timestamp=time)