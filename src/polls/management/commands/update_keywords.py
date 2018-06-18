from django.core.management.base import BaseCommand
from polls.models import Poll


class Command(BaseCommand):
    help = "Migrates keywords for polls from table PollKeyword"

    def handle(self, *args, **options):

        for poll in Poll.objects.filter(is_active=True):
            keywords = [p.keyword.title for p in
                        poll.keywords.filter(
                            is_active=True).select_related('keyword')]
            poll.keywords_array = keywords
            poll.save()
            print "ok"

