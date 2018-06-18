# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth import get_user_model
from polls.models import Poll
from moderators.models import Article
from utils import location_utils
from utils.time_utils import get_timestamp_in_milli
from tasks import add_to_statistics
from .search import UserStatIndex

User = get_user_model()


class UserStatManager(models.Manager):
    """
    User stat manager
    """
    def add_stat(self, request, user_id="", poll_id=None,
                 poll_created=False, poll_answered=False,
                 poll_viewed=False, user_created=False,
                 article_id=None, widget=False):
        agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        remote_address = location_utils.get_client_ip(request)
        add_to_statistics(agent=agent,
                          location=remote_address,
                          referer=referer,
                          user=user_id,
                          poll_id=poll_id,
                          article_id=article_id,
                          user_created=user_created,
                          poll_created=poll_created,
                          poll_answered=poll_answered,
                          poll_viewed=poll_viewed,
                          widget=widget)


class UserStat(models.Model):
    poll = models.ForeignKey(Poll, related_name='statistics', null=True)
    article = models.ForeignKey(Article, related_name='statistics', null=True)
    user = models.CharField(max_length=400, blank=True)
    agent = models.CharField(max_length=400, blank=True)
    referer = models.CharField(max_length=400, blank=True)
    location = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    timestamp = models.BigIntegerField(default=0,
                                       verbose_name=u"Время последнего изменения")
    poll_viewed = models.BooleanField(default=False,
                                      verbose_name=u"Просмотрен")
    poll_answered = models.BooleanField(default=False,
                                        verbose_name=u"Отвечен")
    poll_created = models.BooleanField(default=False,
                                       verbose_name=u"Создание опроса")
    user_created = models.BooleanField(default=False,
                                       verbose_name=u"Создание пользователя")
    widget = models.BooleanField(default=False, verbose_name=u"Виджет?")
    date_added = models.DateTimeField(auto_now_add=True)
    objects = UserStatManager()

    def __unicode__(self):
        return u"agent={0} referer={1} location={2}".format(self.agent,
                                                            self.referer,
                                                            self.location)

    def full(self):
        return {
            "id": self.id,
            "poll": self.poll,
            "article": self.article,
            "user": self.user,
            "location": self.location,
            "agent": self.agent,
            "referer": self.referer,
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "timestamp": self.timestamp,
            "poll_viewed": self.poll_viewed,
            "poll_answered": self.poll_answered,
            "poll_created": self.poll_created,
            "user_created": self.user_created,
            "widget": self.widget
        }

    def indexing(self):
        poll = self.poll.id if self.poll else None
        article = self.article.id if self.article else None
        obj = UserStatIndex(
            meta={'id': self.id},
            poll=poll,
            article=article,
            user=self.user,
            agent=self.agent,
            referer=self.referer,
            location=self.location,
            city=self.city,
            region=self.region,
            country=self.country,
            timestamp=self.timestamp,
            poll_viewed=self.poll_viewed,
            poll_answered=self.poll_answered,
            poll_created=self.poll_created,
            user_created=self.user_created,
            widget=self.widget,
            date_added=self.date_added
        )
        obj.save()
        return obj.to_dict(include_meta=True)

    def save(self, *args, **kwargs):
        self.timestamp = get_timestamp_in_milli()
        super(UserStat, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Статистика"
        verbose_name_plural = u"Статистика"
