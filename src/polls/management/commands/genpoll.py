from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from os import listdir
from os.path import isfile, join
from polls.models import Poll, PollChoice, Category, PollCategory
from random import randint
from utils.Constants import APPROVED
from utils.time_utils import get_timestamp_in_milli
import random

User = get_user_model()
PHOTO_PATH = 'files/photos/'


class Command(BaseCommand):
    help = 'Generates random polls in database'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, default=1)
        parser.add_argument('poll_type', type=int, default=0)

    def get_random_user(self):
        users = User.objects.filter(is_admin=False)
        if len(users) == 0:
            return None
        return random.choice(users)

    def get_random_title(self):
        f = open('files/titles.txt', 'r')
        titles = f.readlines()
        f.close()
        return random.choice(titles)

    def get_random_choice(self):
        f = open('files/choices.txt', 'r')
        choices = f.readlines()
        f.close()
        return random.choice(choices)

    def get_random_keyword(self):
        f = open('files/keywords.txt', 'r')
        keyword = f.readlines()
        f.close()
        return random.choice(keyword)

    def get_random_photo_name(self):
        onlyfiles = [f for f in listdir(PHOTO_PATH) if isfile(join(PHOTO_PATH, f))]
        return random.choice(onlyfiles)

    def add_random_category(self, poll):
        for x in range(0, randint(1, 3)):
            category = Category.objects.filter(is_active=True).order_by("?").first()
            PollCategory.objects.get_or_create(poll=poll, category=category)
            if category.id not in poll.category_ids:
                poll.category_ids.append(category.id)

    def add_random_keyword(self, poll):
        for x in range(0, randint(1, 3)):
            keyword = self.get_random_keyword()
            if keyword not in poll.keywords_array:
                poll.keywords_array.append(keyword)

    def generate_random_ranking_scale(self):
        user = self.get_random_user()
        title = self.get_random_title()
        poll = Poll(user=user, title=title)
        poll.timestamp = get_timestamp_in_milli()
        poll.date_begin = get_timestamp_in_milli() + 60000 * 60 * 24 * (random.randint(0, 4) - 2)
        poll.date_end = poll.date_begin + 60000 * 60 * 24 * random.randint(5, 30)
        poll.paid = False
        poll.min_value = "Bad"
        poll.max_value = "Good"
        poll.is_active = True
        poll.poll_type = 0
        poll.total_answered_count = 0
        poll.status = APPROVED
        photo_name = self.get_random_photo_name()
        poll.image.save(str(get_timestamp_in_milli()) + photo_name,
            File(open(PHOTO_PATH + photo_name, 'r')))
        poll.save()
        for i in xrange(5):
            new_choice = PollChoice()
            new_choice.poll = poll
            new_choice.rs_value = i + 1
            new_choice.priority = i + 1
            new_choice.timestamp = get_timestamp_in_milli()
            new_choice.save()
        self.add_random_category(poll)
        self.add_random_keyword(poll)
        poll.save()
        return poll

    def generate_random_single_choice(self):
        user = self.get_random_user()
        title = self.get_random_title()
        poll = Poll(user=user, title=title)
        poll.timestamp = get_timestamp_in_milli()
        poll.date_begin = get_timestamp_in_milli() + 60000 * 60 * 24 * (random.randint(0, 4) - 2)
        poll.date_end = poll.date_begin + 60000 * 60 * 24 * random.randint(5, 30)
        poll.paid = False
        poll.is_active = True
        poll.poll_type = 1
        poll.total_answered_count = 0
        poll.status = APPROVED
        photo_name = self.get_random_photo_name()
        poll.image.save(str(get_timestamp_in_milli()) + photo_name,
            File(open(PHOTO_PATH + photo_name, 'r')))
        poll.save()
        choice_count = random.randint(3, 10)
        for i in xrange(choice_count):
            new_choice = PollChoice()
            new_choice.poll = poll
            new_choice.sc_value = self.get_random_choice()
            new_choice.priority = i + 1
            new_choice.timestamp = get_timestamp_in_milli()
            new_choice.save()
        self.add_random_category(poll)
        self.add_random_keyword(poll)  
        poll.save()
        return poll

    def generate_random_multiple_choice(self):
        poll = self.generate_random_single_choice()
        poll.poll_type = 2
        poll.save()
        return poll

    def handle(self, *args, **options):
        for i in xrange(options['count']):
            if options['poll_type'] == 0:
                self.generate_random_ranking_scale()
            elif options['poll_type'] == 1:
                self.generate_random_single_choice()
            else:
                self.generate_random_multiple_choice()

        self.stdout.write("Successfully generated {0} polls".format(options['count']))

