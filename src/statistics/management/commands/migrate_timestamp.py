from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from statistics.models import UserStat


class Command(BaseCommand):
    help = 'Maps Indexes'

    def handle(self, *args, **options):
        for stat in UserStat.objects.all():
            stat.date_added = datetime.fromtimestamp(stat.timestamp/1000)
            stat.save()
        self.stdout.write("Successfully finished migration")
