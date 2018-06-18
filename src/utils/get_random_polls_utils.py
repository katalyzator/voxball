from django.db.models import Max
from polls.models import Poll
from random import randint

def get_random_polls(number):
    max_ = Poll.objects.aggregate(Max('id'))['id__max']
    i = 0
    polls = []
    while i < number:
       try:
           polls.append(model.objects.get(pk=randint(1, max_)).full())
           i += 1
       except model.DoesNotExist:
           pass
    return polls