from statistics.models import UserStat
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=UserStat)
def index_user_stat(sender, instance, **kwargs):
    try:
        instance.indexing()
    except:
        pass
