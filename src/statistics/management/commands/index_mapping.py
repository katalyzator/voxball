from django.core.management.base import BaseCommand, CommandError
from statistics.search import UserStatIndex


class Command(BaseCommand):
    help = 'Maps Indexes'

    def handle(self, *args, **options):
        UserStatIndex.init()
        self.stdout.write("Successfully mapped indexes")
