from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from os import listdir
from os.path import isfile, join
from polls.models import Poll, PollChoice, Category, PollCategory
from moderators.models import PollTemplate, PollChoiceTemplate, \
    PollTemplateCategory
from random import randint
from utils.Constants import APPROVED
from utils.time_utils import get_timestamp_in_milli
import random

User = get_user_model()
PHOTO_PATH = 'files/photos/'


class Command(BaseCommand):
    help = 'Generates random templates for polls in database'

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

    def add_random_category(self, poll_temp):
        for x in range(0, randint(1, 3)):
            category = Category.objects.filter(is_active=True).order_by("?").first()
            PollTemplateCategory.objects.get_or_create(poll=poll_temp,
                                                       category=category)
            if category.id not in poll_temp.category_ids:
                poll_temp.category_ids.append(category.id)

    def add_random_keyword(self, poll_temp):
        for x in range(0, randint(1, 3)):
            keyword = self.get_random_keyword()
            if keyword not in poll_temp.keywords_array:
                poll_temp.keywords_array.append(keyword)

    def generate_random_ranking_scale(self):
        user = self.get_random_user()
        title = self.get_random_title()
        poll_temp = PollTemplate(user=user, title=title)
        poll_temp.timestamp = get_timestamp_in_milli()
        poll_temp.date_begin = get_timestamp_in_milli() + 60000 * 60 * 24 * (random.randint(0, 4) - 2)
        poll_temp.date_end = poll_temp.date_begin + 60000 * 60 * 24 * random.randint(5, 30)
        poll_temp.paid = False
        poll_temp.min_value = "Bad"
        poll_temp.max_value = "Good"
        poll_temp.is_active = True
        poll_temp.poll_type = 0
        poll_temp.total_answered_count = 0
        poll_temp.status = APPROVED
        photo_name = self.get_random_photo_name()
        poll_temp.image.save(str(get_timestamp_in_milli()) + photo_name,
            File(open(PHOTO_PATH + photo_name, 'r')))
        poll_temp.save()
        for i in xrange(5):
            new_choice = PollChoiceTemplate()
            new_choice.poll = poll_temp
            new_choice.rs_value = i + 1
            new_choice.priority = i + 1
            new_choice.timestamp = get_timestamp_in_milli()
            new_choice.save()
        self.add_random_category(poll_temp)
        self.add_random_keyword(poll_temp)
        poll_temp.save()
        return poll_temp

    def generate_random_single_choice(self):
        user = self.get_random_user()
        title = self.get_random_title()
        poll_temp = PollTemplate(user=user, title=title)
        poll_temp.timestamp = get_timestamp_in_milli()
        poll_temp.date_begin = get_timestamp_in_milli() + 60000 * 60 * 24 * (random.randint(0, 4) - 2)
        poll_temp.date_end = poll_temp.date_begin + 60000 * 60 * 24 * random.randint(5, 30)
        poll_temp.paid = False
        poll_temp.is_active = True
        poll_temp.poll_type = 1
        poll_temp.total_answered_count = 0
        poll_temp.status = APPROVED
        photo_name = self.get_random_photo_name()
        poll_temp.image.save(str(get_timestamp_in_milli()) + photo_name,
            File(open(PHOTO_PATH + photo_name, 'r')))
        poll_temp.save()
        choice_count = random.randint(3, 10)
        for i in xrange(choice_count):
            new_choice = PollChoiceTemplate()
            new_choice.poll = poll_temp
            new_choice.sc_value = self.get_random_choice()
            new_choice.priority = i + 1
            new_choice.timestamp = get_timestamp_in_milli()
            new_choice.save()
        self.add_random_category(poll_temp)
        self.add_random_keyword(poll_temp)
        poll_temp.save()
        return poll_temp

    def generate_random_multiple_choice(self):
        poll_temp = self.generate_random_single_choice()
        poll_temp.poll_type = 2
        poll_temp.save()
        return poll_temp

    def handle(self, *args, **options):
        for i in xrange(options['count']):
            if options['poll_type'] == 0:
                self.generate_random_ranking_scale()
            elif options['poll_type'] == 1:
                self.generate_random_single_choice()
            else:
                self.generate_random_multiple_choice()

        self.stdout.write("Successfully generated {0} templates".format(options['count']))

