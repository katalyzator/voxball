# -*- coding: utf-8 -*-
from authe.models import City, Country
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db import IntegrityError
from django.db.models.aggregates import Count
from mptt.models import MPTTModel, TreeForeignKey
from random import randint
from utils import location_utils, Constants
from utils.password import generate_poll_private_code
from utils.time_utils import get_timestamp_in_milli
from utils.string_utils import zero_div
from utils.Constants import WEB, DEVICES, RATING_SCALE_COUNT, STATUS_TYPES, \
    UNKNOWN
from django.db import transaction
from utils.facebook import get_likes_info
from utils.image_utils import get_cdn_url
import json
import logging
import uuid
from pytils.translit import slugify

logger = logging.getLogger(__name__)

User = get_user_model()


class PollManager(models.Manager):
    def get_queryset(self):
        return super(PollManager, self).get_queryset().filter(is_delete=False)

    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        if count > 0:
            random_index = randint(0, count - 1)
            return self.all()[random_index]
        else:
            return None

    def create_poll(self, request, user, title, poll_type,
                    date_begin, date_end, min_value, max_value,
                    image, partner_url, facebook_image, category_ids, keywords_array,
                    choices_array, category_id, video, comment_status, private_survey):
        ip = location_utils.get_client_ip(request)
        country_code_mapping = json.loads(open(
            settings.PATH_TO_COUNTRY_CODE_MAPPING).read())
        location = location_utils.get_location(ip)
        country_name = country_code_mapping.get(
            location.get('country', ''), '')
        country, _ = Country.objects.get_or_create(
            name=country_name, code=location.get('country', ''))
        city, _ = City.objects.get_or_create(name=location.get('city', ''),
                                             country=country)
        tries = 0
        partner_author = ''
        if user.profile_type == 1:
            partner_author = user.partner_author
        while True:
            tries += 1
            if tries > Constants.POLL_CODE_MAX_RETRIES:
                raise Exception(u"Max Retries exceed")
            try:
                new_poll = Poll.objects.create(
                    user=user, title=title, poll_type=poll_type,
                    date_begin=date_begin, date_end=date_end,
                    min_value=min_value, max_value=max_value,
                    category_ids=category_ids, keywords_array=keywords_array,
                    city=city,
                    partner_url=partner_url,
                    partner_author=partner_author,
                    choices_array=choices_array,
                    timestamp=get_timestamp_in_milli(),
                    category_id=category_id,
                    private_code=generate_poll_private_code(),
                    video=video, comment_status=comment_status, private_survey=private_survey)
                if image:
                    new_poll.image.save(str(uuid.uuid4()) + '.jpg', image)
                if facebook_image:
                    new_poll.facebook_image.save(str(uuid.uuid4()) + '.jpg', facebook_image)
                break
            except IntegrityError:
                continue
        return new_poll


class Poll(models.Model):
    """
    Main model for polls
    """
    user = models.ForeignKey(User, related_name='polls')
    title = models.CharField(max_length=1000, verbose_name=u"Заголовок",
                             db_index=True)
    image = models.ImageField(upload_to='poll_avatars', blank=True, null=True,
                              height_field='image_height',
                              width_field='image_width',
                              verbose_name=u"Изображение опроса")

    video = models.CharField(max_length=255, verbose_name=u"Ссылка на видео", blank=True, null=True)

    facebook_image = models.ImageField(
        upload_to='poll_facebook_avatars', blank=True,
        height_field='fb_image_height', width_field='fb_image_width',
        null=True, verbose_name=u"Изображение опроса для facebook")
    timestamp = models.BigIntegerField(
        default=0, db_index=True, verbose_name=u"Время последнего изменения")
    date_begin = models.BigIntegerField(default=0, db_index=True,
                                        verbose_name=u"Дата начала опросника")
    date_end = models.BigIntegerField(default=0, db_index=True,
                                      verbose_name=u"Дата окончания опросника")
    paid = models.BooleanField(default=False,
                               verbose_name=u"Оплаченный опрос?")
    min_value = models.CharField(max_length=200, blank=True, null=True,
                                 verbose_name=u"Мин значение для rating_scale")
    max_value = models.CharField(
        max_length=200, blank=True,
        null=True, verbose_name=u"Макс значение для rating_scale")
    comment_status = models.BooleanField(default=False, verbose_name=u"Разрешение на комментарий")
    is_active = models.BooleanField(default=True, db_index=True)
    is_template = models.BooleanField(default=False, db_index=True,
                                      verbose_name=u"Шаблон?")
    rank = models.FloatField(default=0, db_index=True,
                             verbose_name=u'Популярность опроса')
    city = models.ForeignKey(settings.CITY_MODEL, blank=True, null=True,
                             verbose_name=u"Город создания")
    category = models.ForeignKey(settings.CATEGORY_MODEL, blank=True,
                                 null=True, verbose_name=u"Город создания")

    # store width & height to get them without PIL
    image_width = models.PositiveIntegerField(default=0)
    image_height = models.PositiveIntegerField(default=0)

    fb_image_width = models.PositiveIntegerField(default=0)
    fb_image_height = models.PositiveIntegerField(default=0)

    RATING_SCALE = 0
    SINGLE_CHOICE = 1
    MULTIPLE_CHOICE = 2

    TYPES = (
        (RATING_SCALE, u"rating scale"),
        (SINGLE_CHOICE, u"single choice"),
        (MULTIPLE_CHOICE, u"multiple choice"),
    )

    poll_type = models.SmallIntegerField(choices=TYPES, default=SINGLE_CHOICE,
                                         db_index=True,
                                         verbose_name=u"Тип опроса")

    private_code = models.CharField(max_length=30,
                                    blank=True,
                                    unique=True,
                                    verbose_name=u"Приватный ключ")

    status = models.SmallIntegerField(choices=STATUS_TYPES, default=UNKNOWN,
                                      db_index=True,
                                      verbose_name=u"Статус опроса")

    total_answered_count = models.IntegerField(
        default=0, verbose_name=u"Общее количество проголосовавших")

    category_ids = ArrayField(models.IntegerField(), default=[], db_index=True,
                              verbose_name=u"Категории")
    keywords_array = ArrayField(models.CharField(max_length=200), default=[],
                                db_index=True, verbose_name=u"Ключевые слова")
    choices_array = ArrayField(models.CharField(max_length=200), default=[],
                               db_index=True, verbose_name=u"Ответы")

    partner_url = models.CharField(max_length=250, default='', verbose_name=u"url партнера")
    partner_author = models.CharField(max_length=250, default='', verbose_name=u"Автор партнера")

    is_delete = models.BooleanField('Удалена', default=False)
    slug = models.SlugField(verbose_name=u"Ссылка", max_length=1000)
    private_survey = models.BooleanField(verbose_name=u"Приватный опрос", default=False)

    objects = PollManager()

    def __unicode__(self):
        return u"id={0} user={1} title={2}".format(self.id, self.user,
                                                   self.title)

    def short(self, user=None, is_admin=False):
        obj = {
            "id": self.id,
            "title": self.title,
            "image_full": {
                'url': get_cdn_url(self.image),
                'width': self.image_width,
                'height': self.image_height
            } if self.image else None,
            "video": self.video,
            "facebook_image_full": {
                'url': get_cdn_url(self.facebook_image),
                'width': self.fb_image_width,
                'height': self.fb_image_height
            } if self.facebook_image else None,
            "date_begin": self.date_begin,
            "date_end": self.date_end,
            "categories": [c.full() for c in self.categories.filter(
                is_active=True).select_related('category')],
            "private_code": self.private_code,
            "slug": self.slug,
            "status": self.status,
            "total_answered_count": self.total_answered_count,
            "comments_enabled": self.comment_status,
            "user": self.user.short(),
            "partner_url": self.partner_url,
            "partner_author": self.partner_author,
        }
        return obj

    def full(self, user=None, is_admin=False, with_fb=False,
             with_categories=True, with_article=False, sel_choice_ids=[]):
        obj = {
            "id": self.id,
            "title": self.title,
            "image_full": {
                'url': get_cdn_url(self.image),
                'width': self.image_width,
                'height': self.image_height
            } if self.image else None,
            "video": self.video,
            "facebook_image_full": {
                'url': get_cdn_url(self.facebook_image),
                'width': self.fb_image_width,
                'height': self.fb_image_height
            } if self.facebook_image else None,
            "timestamp": self.timestamp,
            "date_begin": self.date_begin,
            "date_end": self.date_end,
            "paid": self.paid,
            "poll_type": self.poll_type,
            "is_active": self.is_active,
            "poll_choices": [c.full() for c in self.choices.filter(
                is_active=True).order_by('priority')],
            "keywords": [k.keyword.title for k in self.keywords.filter(
                is_active=True).select_related('keyword')],
            "total_answered_count": self.total_answered_count,
            "status": self.status,
            "rank": self.rank,
            "is_own": True if user and self.user == user else False,
            "city": self.city.short() if self.city else None,
            "private_code": self.private_code,
            "slug": self.slug,
            "comments_enabled": self.comment_status,
            "user": self.user.short(),
            "partner_url": self.partner_url,
            "partner_author": self.partner_author,
            "category": (self.category.full(with_children=False)
                         if self.category else None),
        }
        """Statistics"""
        if sel_choice_ids:
            obj["poll_choices"] = PollChoice.objects.mark_answered_choices(
                obj["poll_choices"], sel_choice_ids)
        total_percent = 0
        total_answered_count = sum(map(lambda x: x["answered_count"],
                                       obj["poll_choices"]))
        total_answered_percent = 0
        for choice in obj["poll_choices"]:
            choice["answer_percent"] = int(
                zero_div(float(choice["answered_count"]),
                         total_answered_count) * 100)
            total_percent += (choice["answer_percent"]
                              if choice["is_answered"] else 0)
            total_answered_percent += choice["answer_percent"]
        obj["poll_choices"][-1]["answer_percent"] += 100 - total_answered_percent
        obj["total_percent"] = total_percent
        """End statistics"""
        if with_article:
            article_poll = self.article_set.filter(is_active=True).first()
            obj["article"] = (article_poll.article.very_short()
                              if article_poll else None)
        if self.date_begin == 0:
            obj["date_begin"] = None
        if self.date_end == 0:
            obj["date_end"] = None
        if self.poll_type == Poll.RATING_SCALE:
            obj["min_value"] = self.min_value
            obj["max_value"] = self.max_value
        if with_fb:
            obj["fb_info"] = get_likes_info(
                settings.POLL_URL.format(id=self.id))
        if with_categories:
            obj["categories"] = [c.full() for c in self.categories.filter(
                is_active=True).select_related('category')]
        return obj

    def save(self, *args, **kwargs):
        # self.timestamp = get_timestamp_in_milli()
        # if not self.private_code:
        #     tries = 0
        #     while True:
        #         tries += 1
        #         if tries > Constants.POLL_CODE_MAX_RETRIES:
        #             raise Exception(u"Max Retries exceed")
        #         try:
        #             self.private_code = generate_poll_private_code()
        #             super(Poll, self).save(*args, **kwargs)
        #             break
        #         except IntegrityError:
        #             continue
        super(Poll, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.title + '-' + str(self.id))
            # super(Poll, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Опрос"
        verbose_name_plural = u"Опросы"


class PollChoiceManager(models.Manager):
    """
    Poll choice manager model
    """

    @transaction.atomic
    def create_sc_choices(self, poll, choices):
        for choice in choices:
            new_choice = PollChoice()
            new_choice.poll = poll
            new_choice.sc_value = choice['value']
            new_choice.priority = int(choice['priority'])
            new_choice.timestamp = get_timestamp_in_milli()
            new_choice.save()

    @transaction.atomic
    def update_sc_choices(self, poll, choices):
        PollChoice.objects.filter(poll=poll).update(is_active=False)
        for ch in choices:
            choice, _ = PollChoice.objects.get_or_create(id=ch.get('id'))
            choice.poll = poll
            choice.is_active = True
            choice.sc_value = ch['value']
            choice.priority = int(ch['priority'])
            choice.timestamp = get_timestamp_in_milli()
            choice.save()

    @transaction.atomic
    def create_rs_choices(self, poll):
        for i in xrange(RATING_SCALE_COUNT):
            new_choice = PollChoice()
            new_choice.poll = poll
            new_choice.rs_value = i + 1
            new_choice.priority = i + 1
            new_choice.timestamp = get_timestamp_in_milli()
            new_choice.save()

    def mark_answered_choices(self, choices_json, selected_choice_ids):
        for choice in choices_json:
            choice["is_answered"] = (True if choice["id"]
                                             in selected_choice_ids else False)
        return choices_json


class PollChoice(models.Model):
    """
    Poll choices model
    """
    poll = models.ForeignKey(Poll, related_name='choices')
    sc_value = models.CharField(max_length=500, blank=True,
                                verbose_name=u"Значение single_choice ответа")
    rs_value = models.SmallIntegerField(
        default=0, blank=True, verbose_name=u"Значение rating_scale ответа")
    is_active = models.BooleanField(default=True, verbose_name=u"Активный?")
    priority = models.SmallIntegerField(default=0, verbose_name=u"Приоритет")
    timestamp = models.BigIntegerField(default=0)
    answered_count = models.IntegerField(
        default=0, verbose_name=u"Количество проголосовавших за этот ответ")

    objects = PollChoiceManager()

    def __unicode__(self):
        return u"id={0} poll={1} is_active={2}".format(self.id, self.poll,
                                                       self.is_active)

    def full(self):
        obj = {
            "id": self.id,
            "priority": self.priority,
            "answered_count": self.answered_count,
            "answer_percent": 0,
            # default
            "is_answered": False
        }
        if self.poll.poll_type == Poll.RATING_SCALE:
            obj["value"] = self.rs_value
        else:
            obj["value"] = self.sc_value
        return obj

    class Meta:
        verbose_name = u"Вариант ответа"
        verbose_name_plural = u"Варианты ответов"


class PollAnswer(models.Model):
    """
    Poll answer model
    """
    user = models.ForeignKey(User, blank=True, null=True,
                             related_name='answers')
    poll = models.ForeignKey(Poll, related_name='answers')
    poll_choice = models.ForeignKey(PollChoice, related_name='choice_answers')

    user_cookie = models.CharField(max_length=200, blank=True, null=True,
                                   verbose_name=u'Сгенерированный куки')
    agent = models.CharField(max_length=200, blank=True, verbose_name=u"Агент")
    referer = models.CharField(max_length=1000, blank=True,
                               verbose_name=u"Референт")
    location = models.CharField(max_length=200)
    location_ip = models.CharField(max_length=50, blank=True,
                                   verbose_name=u"ip-адрес")
    location_country = models.CharField(max_length=200, blank=True,
                                        verbose_name=u'Страна')
    location_region = models.CharField(max_length=200, blank=True,
                                       verbose_name=u'Регион')
    location_city = models.CharField(max_length=200, blank=True,
                                     verbose_name=u'Город')
    source = models.SmallIntegerField(choices=DEVICES, default=WEB,
                                      verbose_name=u"Источник ответа")

    is_active = models.BooleanField(default=True)
    timestamp = models.BigIntegerField(default=0)

    def __unicode__(self):
        return u"id={0} poll={1} poll_choice={2}".format(self.id, self.poll,
                                                         self.poll_choice)

    def full(self):
        result = {
            "id": self.id,
            "is_active": self.is_active,
            "poll_choice_id": self.poll_choice.id,
            "agent": self.agent,
            "referer": self.referer,
            "location": self.location,
            "location_ip": self.location_ip,
            "location_country": self.location_country,
            "location_region": self.location_region,
            "location_city": self.location_city,
            "source": self.source,
            "timestamp": self.timestamp,
        }
        return result

    class Meta:
        verbose_name = u"Ответ пользователя"
        verbose_name_plural = u"Ответы пользователей"


class Category(MPTTModel):
    name = models.CharField(max_length=200, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']
        verbose_name = u"Категория"
        verbose_name_plural = u"Категории"

    class Meta:
        verbose_name = u"Категория"
        verbose_name_plural = u"Категория"

    def full(self, with_children=True):
        result = {
            "id": self.pk,
            "name": self.name,
        }
        if with_children and self.children.filter(is_active=True).count() > 0:
            result["subcategories"] = [c.full(with_children=False)
                                       for c in self.children.filter(
                    is_active=True)]
        else:
            result["subcategories"] = []
        return result

    def __unicode__(self):
        return self.name

    def short(self):
        return {
            "id": self.pk,
            "name": self.name
        }


class Keyword(models.Model):
    """
    Keywords model
    """
    category = models.ForeignKey(Category, null=True, related_name='keywords')
    title = models.CharField(max_length=200, unique=True)
    rank = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=False)

    def full(self):
        result = {
            "id": self.id,
            "title": self.title
        }
        if self.category:
            result["category"] = self.category.short()
        return result

    def __unicode__(self):
        return u"id={0} title={1} category={2}".format(self.id, self.title,
                                                       self.category)

    class Meta:
        verbose_name = u"Ключевое слово"
        verbose_name_plural = u"Ключевые слова"


class PollCategoryManager(models.Manager):
    """
    Poll category manager
    """

    def add_categories(self, poll, categories):
        if categories:
            self.filter(poll=poll).exclude(
                category__in=categories).update(is_active=False)
            for category in categories:
                new_category, _ = self.get_or_create(poll=poll,
                                                     category=category)
                new_category.is_active = True
                new_category.save()


class PollCategory(models.Model):
    """
    Poll category entry
    """
    poll = models.ForeignKey(Poll, related_name='categories')
    category = models.ForeignKey(Category, related_name='polls')
    is_active = models.BooleanField(default=True)

    objects = PollCategoryManager()

    def full(self):
        return self.category.short()

    def __unicode__(self):
        return u"id={0} poll={1} category={2}".format(self.id, self.poll,
                                                      self.category)

    class Meta:
        unique_together = ('poll', 'category')
        verbose_name = u"Ключевая категория опроса"
        verbose_name_plural = u"Ключевые категории опросов"


class PollKeywordManager(models.Manager):
    """
    Poll keyword manager
    """

    @transaction.atomic
    def add_keywords(self, poll, keywords):
        poll.keywords.filter(is_active=True).update(is_active=False)
        for keyword in keywords:
            keyword, _ = Keyword.objects.get_or_create(title=keyword)
            keyword.is_active = True
            keyword.rank += 1
            keyword.save()
            new_keyword, _ = PollKeyword.objects.get_or_create(poll=poll,
                                                               keyword=keyword)
            new_keyword.is_active = True
            new_keyword.save()


class PollKeyword(models.Model):
    """
    Poll keywords entry
    """
    poll = models.ForeignKey(Poll, related_name='keywords')
    keyword = models.ForeignKey(Keyword, blank=True, null=True, db_index=True,
                                verbose_name=u'Тег')

    is_active = models.BooleanField(default=True)
    timestamp = models.BigIntegerField(default=0)

    objects = PollKeywordManager()

    def full(self):
        return {
            "id": self.id,
            "keyword": self.keyword
        }

    def __unicode__(self):
        return u"id={0} poll={1} keyword={2}".format(self.id, self.poll,
                                                     self.keyword)

    class Meta:
        verbose_name = u"Ключевое слово опроса"
        verbose_name_plural = u"Ключевые слова опросов"


class UserCategoryManager(models.Manager):
    """
    User category manager
    """

    @transaction.atomic
    def add_categories(self, user, category_ids):
        self.filter(user=user).update(is_active=False)
        user.category_ids = []
        for category_id in category_ids:
            user_category, created = self.get_or_create(
                user=user, category_id=category_id)
            user_category.is_active = True
            user_category.save()
            user.category_ids.append(category_id)
        user.save()


class UserCategory(models.Model):
    """
    User & category entry
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='categories')
    category = models.ForeignKey(Category)
    count = models.PositiveIntegerField(default=0,
                                        verbose_name=u"Новых постов")
    is_active = models.BooleanField(default=True, db_index=True)
    objects = UserCategoryManager()

    def short(self):
        return {
            'id': self.id,
            'count': self.count,
            'category': self.category.short()
        }

    def __unicode__(self):
        return u"id: %s user: %s category: %s" % (self.id, self.user,
                                                  self.category)

    class Meta:
        index_together = ('user', 'category')
        unique_together = ('user', 'category')
        verbose_name = u"Категория пользователя"
        verbose_name_plural = u"Категории пользователя"


class PollComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='comment_user')

    poll = models.ForeignKey(settings.POLL_MODEL,
                             related_name='poll_comment')

    comment = models.TextField(verbose_name=u"Комментарий")
    active = models.BooleanField(default=False,
                                 verbose_name=u"Поставьте галочку, чтобы отобразить комментарий на сайте")

    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def full(self):
        result = {
            "id": self.id,
            "user": self.user,
            "poll": self.poll,
            "comment": self.comment,
            "created_at": self.timestamp,
        }
        return result

    class Meta:
        verbose_name = u"Комментарий опроса"
        verbose_name_plural = u"Комментарии опросов"
        ordering = ['-timestamp']
