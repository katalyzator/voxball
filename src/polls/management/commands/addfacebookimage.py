from django.core.management.base import BaseCommand, CommandError
from polls.models import Poll
from utils.image_utils import get_texted_image
import logging


class Command(BaseCommand):
    help = "Creates facebook_image for polls without facebook_image"

    def add_arguments(self, parser):
        parser.add_argument('poll_id', type=int, default=0)

    def handle(self, *args, **options):
        if options['poll_id'] == 0:
            polls = Poll.objects.exclude(image='')
        else:
            polls = Poll.objects.filter(id=options['poll_id']).exclude(image='')
        for poll in polls:
            try:
                poll.facebook_image = get_texted_image(poll.image, poll.title)
                poll.save()
                self.stdout.write("Successfully created facebook_image for poll with id {0}".format(poll.id))
            except Exception as e:
                self.stderr.write("Error in creating facebook_image with id {0} with message {1}".format(poll.id, str(e)))

        self.stdout.write("Successfully created facebook_image for all polls in database")
