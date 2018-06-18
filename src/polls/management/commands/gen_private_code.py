from django.core.management.base import BaseCommand
from polls.models import Poll


class Command(BaseCommand):
    help = "Generates private codes for all polls"

    def handle(self, *args, **options):
        polls = Poll.objects.all()
        self.stderr.write(u"Total: {}".format(polls.count()))
        for poll in polls:
            try:
                poll.private_code = ""
                poll.save()
            except Exception as e:
                self.stderr.write("Error in generating code for poll id {0} with message {1}".format(poll.id, str(e)))
        self.stdout.write("Successfully generated codes for polls")
