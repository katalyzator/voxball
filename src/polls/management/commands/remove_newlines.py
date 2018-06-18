from django.core.management.base import BaseCommand
from polls.models import Poll, PollChoice


class Command(BaseCommand):
    help = "Removes newlines from poll titles and choices"

    def handle(self, *args, **options):
        for poll in Poll.objects.all():
            poll.title = poll.title.replace(u'\n', "")
            poll.save()

        for pc in PollChoice.objects.all():
            pc.sc_value = pc.sc_value.replace(u'\n', "")
            pc.save()

