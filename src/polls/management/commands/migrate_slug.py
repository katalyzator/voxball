from django.core.management.base import BaseCommand
from polls.models import Poll
from pytils.translit import slugify


class Command(BaseCommand):
    help = "Migrates slugs for polls"

    def handle(self, *args, **options):

        for poll in Poll.objects.all():
            poll.slug = slugify(poll.title + '-' + str(poll.id))
            poll.save()
            # if not poll.slug:
