from django.core.management.base import BaseCommand
from polls.models import Poll
from moderators.models import PollTemplate


class Command(BaseCommand):
    help = "Migrates category_ids for polls from table PollCategory"

    def handle(self, *args, **options):

        for poll in Poll.objects.filter(is_active=True):
            p_category = poll.categories.filter(is_active=True).first()
            if p_category:
                poll.category = p_category.category
                poll.save()

        for poll in PollTemplate.objects.filter(is_active=True):
            p_category = poll.categories.filter(is_active=True).first()
            if p_category:
                poll.category = p_category.category
                poll.save()
