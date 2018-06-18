# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from polls.models import Poll, PollChoice, PollChoiceManager, Category
from utils.time_utils import get_timestamp_in_milli


class PollTemplate(Poll):
    """
    Templates model for polls
    """

    def full(self):
        result = super(PollTemplate, self).full(is_admin=True,
                                                with_categories=False)
        result['is_template'] = True
        result["categories"] = [c.full() for c in self.template_categories.filter(is_active=True).select_related('category')]
        result['date_begin'] = None
        result['date_end'] = None
        return result

    class Meta:
        verbose_name = u"Шаблон опросов"
        verbose_name_plural = u"Шаблоны опроса"


class PollChoiceTemplateManager(PollChoiceManager):
    """
    Poll choice template manager
    """
    @transaction.atomic
    def create_sc_choices(self, poll, choices):
        for choice in choices:
            new_choice = PollChoiceTemplate()
            new_choice.poll = poll
            new_choice.sc_value = choice['value']
            new_choice.priority = int(choice['priority'])
            new_choice.timestamp = get_timestamp_in_milli()
            new_choice.save()


class PollChoiceTemplate(PollChoice):
    """
    Templates model for poll choices
    """

    objects = PollChoiceTemplateManager()

    class Meta:
        verbose_name = u"Шаблон ответа опросов"
        verbose_name_plural = u"Шаблоны ответов опросов"


class PollTemplateCategoryManager(models.Manager):
    """
    Poll category manager
    """

    def add_categories(self, poll, categories):
        self.filter(poll=poll).exclude(category__in=categories).update(is_active=False)
        for category in categories:
            new_category, _ = self.get_or_create(poll=poll, category=category)
            new_category.is_active = True
            new_category.save()


class PollTemplateCategory(models.Model):
    """
    Poll template category entry
    """
    poll = models.ForeignKey(PollTemplate, related_name='template_categories')
    category = models.ForeignKey(Category, related_name='template_polls')
    is_active = models.BooleanField(default=True)

    objects = PollTemplateCategoryManager()

    def full(self):
        return self.category.short()

    def __unicode__(self):
        return u"id={0} poll={1} category={2}".format(self.id, self.poll,
                                                      self.category)

    class Meta:
        verbose_name = u"Ключевая категория шаблона"
        verbose_name_plural = u"Ключевые категории шаблонов"


class Article(models.Model):
    """
    Model for articles
    """
    title = models.CharField(max_length=1000, blank=True,
                             verbose_name=u"Заголовок")
    article_url = models.CharField(max_length=1000, unique=True,
                                   verbose_name=u"URL статьи")
    poll_ids = ArrayField(models.IntegerField(), default=[], blank=True,
                          verbose_name=u"ID опросов")
    keywords = ArrayField(models.CharField(max_length=100), default=[],
                          blank=True, verbose_name=u"Теги опросов")
    icon = models.ImageField(blank=True, null=True, verbose_name=u"Иконка")
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"id=%s article_url=%s" % (self.id, self.article_url)

    def very_short(self):
        return {
            "article_url": self.article_url,
            "icon": self.icon.url if self.icon else "",
        }

    def short(self):
        return {
            "id": self.id,
            "article_url": self.article_url,
            "title": self.title,
            "icon": self.icon.url if self.icon else "",
            "keywords": self.keywords
        }

    def full(self):
        return {
            "id": self.id,
            "title": self.title,
            "article_url": self.article_url,
            "icon": self.icon.url if self.icon else "",
            "polls": [{"id": x.poll.id,
                       "user": x.poll.user.short(),
                       "title": x.poll.title,
                       "date_begin": x.poll.date_begin,
                       } for x in self.poll_entry_set.filter(
                is_active=True).select_related("poll")],
            "keywords": self.keywords,
        }

    class Meta:
        verbose_name = u"Статья"
        verbose_name_plural = u"Статьи"


class ArticlePollEntry(models.Model):
    """
    """
    article = models.ForeignKey(Article, related_name="poll_entry_set")
    poll = models.ForeignKey(settings.POLL_MODEL, related_name="article_set")
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"id=%s poll=%s article=%s" % (self.id, self.poll, self.article)

    class Meta:
        verbose_name = u"Опрос статьи"
        verbose_name_plural = u"Опросы статьи"
