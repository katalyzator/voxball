from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from os import listdir
from os.path import isfile, join
from polls.models import Poll, PollChoice, PollAnswer, PollChoice
from utils.time_utils import get_timestamp_in_milli
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Checks all polls in database for statistic'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', type=int, default=0)

    def get_username_from_poll_answer(self, poll_answer):
        try:
            return poll_answer.user.username
        except:
            return None

    def get_cookie_from_poll_answer(self, poll_answer):
        try:
            return poll_answer.user_cookie
        except:
            return None

    def get_user_from_poll_answer(self, poll_answer):
        return (self.get_username_from_poll_answer(poll_answer),
                self.get_cookie_from_poll_answer(poll_answer))

    def check_single_choice_poll(self, poll):
        poll_answers = [poll_answer for poll_answer in PollAnswer.objects.filter(is_active=True, poll=poll)]
        x = [self.get_user_from_poll_answer(x) for x in poll_answers]
        unique_answers = set(x)
        if len(unique_answers) != len(poll_answers):
            return False, "not unique users, poll_answers: {0} unique_answers: {1}".format(x, unique_answers)
        if poll.total_answered_count != len(poll_answers):
            return False, "total answered count not correct"
        choices = PollChoice.objects.filter(is_active=True, poll=poll)
        for choice in choices:
            if choice.answered_count != PollAnswer.objects.filter(is_active=True, poll=poll, poll_choice=choice).count():
                return False, "poll choice answered count not correct"
        return True, "ok"

    def check_multiple_choice_poll(self, poll):
        poll_answers = [poll_answer for poll_answer in PollAnswer.objects.filter(is_active=True, poll=poll)]
        x = [self.get_user_from_poll_answer(x) for x in poll_answers]
        unique_answers = set(x)
        if poll.total_answered_count != len(unique_answers):
            return False, "total answered count not correct"
        choices = PollChoice.objects.filter(is_active=True, poll=poll)
        for choice in choices:
            if choice.answered_count != PollAnswer.objects.filter(is_active=True, poll=poll, poll_choice=choice).count():
                return False, "poll choice answered count not correct"
        return True, "ok"

    def handle_poll_choices(self, poll):
        choices = PollChoice.objects.filter(is_active=True, poll=poll)
        for choice in choices:
            choice.answered_count = 0
            choice.save()
        for poll_answer in PollAnswer.objects.filter(is_active=True,
                                                     poll=poll):
            choice = poll_answer.poll_choice
            choice.answered_count = choice.answered_count + 1
            choice.save()

    def handle_single_choice_poll(self, poll):
        poll_answers = [poll_answer for poll_answer in PollAnswer.objects.filter(is_active=True, poll=poll)]
        poll.total_answered_count = len(poll_answers)
        poll.save()
        self.handle_poll_choices(poll)

    def handle_multiple_choice_poll(self, poll):
        poll_answers = [poll_answer for poll_answer in PollAnswer.objects.filter(is_active=True, poll=poll)]
        x = [self.get_user_from_poll_answer(x) for x in poll_answers]
        unique_answers = set(x)
        poll.total_answered_count = len(unique_answers)
        poll.save()
        self.handle_poll_choices(poll)

    def handle(self, *args, **options):
        self.stdout.write("Checking {0} polls".format(Poll.objects.filter(is_active=True).count()))
        polls = Poll.objects.filter(is_active=True)
        if options['poll_id'] != 0:
            polls = Poll.objects.filter(is_active=True, id=options['poll_id'])
        cnt = 1
        for poll in polls:
            if poll.poll_type != 2:
                verdict, msg = self.check_single_choice_poll(poll)
                self.stdout.write("{3}. verdict={0} message={1} poll_id={2}".format(verdict, msg, poll.id, cnt))
                retries = 0
                if not verdict:
                    while retries < 3 and not verdict:
                        retries += 1
                        self.handle_single_choice_poll(poll)
                        verdict, msg = self.check_single_choice_poll(poll)
                    if verdict:
                        self.stdout.write("Successfully handled error on poll with id={0}".format(poll.id))
                    else:
                        self.stdout.write("ERROR while handling poll with id={0}".format(poll.id))
            else:
                verdict, msg = self.check_multiple_choice_poll(poll)
                self.stdout.write("{3}. verdict={0} message={1} poll_id={2}".format(verdict, msg, poll.id, cnt))
                retries = 0
                if not verdict:
                    while retries < 3 and not verdict:
                        retries += 1
                        self.handle_multiple_choice_poll(poll)
                        verdict, msg = self.check_multiple_choice_poll(poll)
                    if verdict:
                        self.stdout.write("Successfully handled error on poll with id={0}".format(poll.id))
                    else:
                        self.stdout.write("ERROR while handling poll with id={0}".format(poll.id))
            cnt += 1

