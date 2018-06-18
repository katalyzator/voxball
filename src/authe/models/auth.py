# -*- coding: utf-8 -*-
from authe import tasks
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
    PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from os import urandom
from utils import time_utils
from utils.Constants import USER_TYPES, EMAIL_REGISTER
from utils.image_utils import get_cdn_url
from utils.messages import PASSWORD_CHANGE_TITLE
from utils.password import generate_password


class MainUserManager(BaseUserManager):
    """
    Main user manager
    """

    def create_user(self, username, password=None, is_active=None):
        """
        Creates and saves a user with the given username and password
        """
        if not username:
            raise ValueError('Users must have an username')
        user = self.model(username=username)
        user.set_password(password)
        user.timestamp = time_utils.get_timestamp_in_milli()
        if is_active is not None:
            user.is_active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given username and password
        """
        user = self.create_user(username, password=password)
        user.email = username
        user.is_admin = True
        user.is_superuser = True
        user.is_moderator = True
        user.save(using=self._db)
        return user

    def all_object(self):
        return self.get_queryset()


class MainUser(AbstractBaseUser, PermissionsMixin):
    """
    Model for storing user, username can be email or facebook id
    """
    username = models.CharField(max_length=100, blank=False, unique=True,
                                db_index=True, verbose_name=u'Username')
    fb_id = models.CharField(max_length=100, blank=True, db_index=True,
                             verbose_name=u"Facebook id")
    full_name = models.CharField(max_length=555, blank=True,
                                 verbose_name=u'Full name')
    email = models.CharField(max_length=50, blank=True, db_index=True,
                             verbose_name=u'Email')
    email_activated = models.BooleanField(default=False,
                                          verbose_name=u'Email activated')
    avatar = models.ImageField(upload_to='user_avatars', blank=True, null=True,
                               height_field='avatar_height',
                               width_field='avatar_width')
    age = models.PositiveIntegerField(null=True, verbose_name=u"Возраст")
    phone = models.CharField(max_length=50, db_index=True, blank=True,
                             verbose_name=u"Телефон")

    user_type = models.SmallIntegerField(
        choices=USER_TYPES, default=EMAIL_REGISTER,
        db_index=True, verbose_name=u"Тип пользователя")

    # store width & height to get them without PIL
    avatar_width = models.PositiveIntegerField(default=0, null=True)
    avatar_height = models.PositiveIntegerField(default=0, null=True)

    poll_count = models.PositiveIntegerField(
        default=0, verbose_name=u'Кол-во опросов')
    answer_count = models.PositiveIntegerField(
        default=0, verbose_name=u'Кол-во ответов')
    repost_count = models.PositiveIntegerField(
        default=0, verbose_name=u'Кол-во репостов')
    rating = models.IntegerField(default=0, verbose_name=u'Рейтинг')

    push_notifications_enabled = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False, verbose_name=u'Admin')
    is_moderator = models.BooleanField(default=False)

    profile_type = models.PositiveIntegerField(default=0, verbose_name=u'Тип профиля')
    partner_type = models.PositiveIntegerField(default=0, verbose_name=u'Тип профиля партнера')
    partner_details = models.CharField(max_length=200, blank=True, verbose_name=u'Реквизиты')
    partner_author = models.CharField(max_length=200, blank=True, verbose_name=u'Партнер / автор')
    partner_phone = models.CharField(max_length=50, blank=True, verbose_name=u"Телефон партнера")

    showable_votem = models.BooleanField(default=False, blank=True, verbose_name=u"Показ всех голосов")

    city = models.ForeignKey(settings.CITY_MODEL, blank=True, null=True)

    category_ids = ArrayField(models.IntegerField(), default=[],
                              verbose_name=u"Список категорий")

    objects = MainUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    timestamp = models.BigIntegerField(default=0)

    def full(self, user=None):
        obj = {
            "id": self.id,
            "timestamp": self.timestamp,
            "age": self.age,
            "phone": self.phone,
            "username": self.username,
            "fb_id": self.fb_id,
            "is_moderator": self.is_moderator,
            "full_name": self.full_name,
            "email": self.email,
            "email_activated": self.email_activated,
            "avatar_full": {
                'url': get_cdn_url(self.avatar),
                'width': self.avatar_width,
                'height': self.avatar_height
            } if self.avatar else None,
            "poll_count": self.poll_count,
            "answer_count": self.answer_count,
            "repost_count": self.repost_count,
            "rating": self.rating,
            "are_poll_results_public": self.showable_votem,
            "profile_type": self.profile_type,
            "partner_type": self.partner_type,
            "partner_details": self.partner_details,
            "partner_author": self.partner_author,
            "partner_phone": self.partner_phone,
            "push_notifications_enabled": self.push_notifications_enabled,
            "categories": [c.short() for c in self.categories.filter(
                is_active=True, category__is_active=True)],
            "city": self.city.short() if self.city else None,
            "user_type": self.user_type,
        }
        return obj

    def short(self, user=None):
        obj = {
            "id": self.id,
            "full_name": self.full_name,
            "profile_type": self.profile_type,
            "partner_type": self.partner_type,
            "partner_author": self.partner_author,
            "partner_phone": self.partner_phone,
            "are_poll_results_public": self.showable_votem,
            "avatar_full": {
                'url': get_cdn_url(self.avatar),
                'width': self.avatar_width,
                'height': self.avatar_height
            } if self.avatar else None,
        }
        return obj

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin or self.is_moderator

    def get_full_name(self):
        return u"{} {}".format(self.username, self.is_active)

    def get_short_name(self):
        return self.username

    def __unicode__(self):
        return self.username

    def email_reset_password(self, token):
        """
        Sends reset password link via email to this User
        """
        link = settings.PASSWORD_RESET_URL.format(token=token)
        email_body = render_to_string('emails/password_reset_link.html',
                                      {
                                          'first_name': self.full_name,
                                          'link': link
                                      })
        tasks.email(self.email, subject=PASSWORD_CHANGE_TITLE,
                    message=email_body)

    def email_password(self, password):
        """
        Sends password via email to this User
        """
        email_body = render_to_string('emails/password_reset.html',
                                      {
                                          'first_name': self.full_name,
                                          'password': password
                                      })
        tasks.email(self.username, subject=u"New password, Votem",
                    message=email_body)

    def generate_new_password(self):
        new_password = generate_password()
        self.set_password(new_password)
        self.save()
        return new_password

    def increment_poll_count(self):
        self.poll_count += 1
        self.save()

    def increment_answer_count(self):
        self.answer_count += 1
        self.save()

    def increment_repost_count(self):
        self.repost_count += 1
        self.save()

    def get_object(self):
        obj = {
            "username": u"{}".format(self.username).encode("utf-8"),
            "email": u"{}".format(self.email).encode("utf-8"),
            "full_name": u"{}".format(self.full_name).encode("utf-8"),
            "age": u"{}".format(self.age).encode("utf-8"),
            "phone": u"{}".format(self.phone).encode("utf-8"),
            "poll_count": u"{}".format(self.poll_count).encode("utf-8"),
            "answer_count": u"{}".format(self.answer_count).encode("utf-8"),
        }

        return obj


class ActivationManager(models.Manager):
    """
    Manager for activation keys.
    """

    def generate(self, username, code=None):
        self.filter(username=username).update(is_active=False)
        key = urandom(settings.ACTIVATION_KEY_LENGTH).encode('hex')
        activation = Activation(username=username, key=key, is_active=True)
        if code:
            activation.code = code
        activation.end_time = (timezone.now()
                               + timedelta(minutes=settings.ACTIVATION_TIME))
        activation.save()
        return key


class Activation(models.Model):
    """
    Model for storing activation keys campaigns.
    """
    key = models.CharField(max_length=200, unique=True, db_index=True)
    username = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    code = models.CharField(max_length=10)
    end_time = models.DateTimeField(blank=True)

    objects = ActivationManager()


class TokenLog(models.Model):
    """
    Token log model
    """
    token = models.CharField(max_length=500, blank=False, null=False)
    user = models.ForeignKey(
        MainUser, blank=False, null=False, related_name='tokens')

    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "token={0}".format(self.token)

    class Meta:
        index_together = [
            ["token", "user"]
        ]


class ResetPasswordRequest(models.Model):
    """
    Request to reset password.
    """
    user = models.ForeignKey('MainUser', blank=False, null=False,
                             related_name='password_resets')
    token = models.CharField(max_length=100, blank=False, null=False)
    deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.token

    class Meta:
        index_together = [
            ["token", "user"]
        ]


class ResetEmailManager(models.Manager):
    """
    Manager for activation keys.
    """

    def generate(self, new_email, user):
        self.filter(new_email=new_email, user=user).update(is_active=False)
        key = urandom(settings.ACTIVATION_KEY_LENGTH).encode('hex')
        reset_email = ResetEmailRequest(new_email=new_email, key=key,
                                        is_active=True, user=user)
        reset_email.save()
        return key


class ResetEmailRequest(models.Model):
    """
    Request to reset password.
    """
    user = models.ForeignKey('MainUser', blank=False, null=False,
                             related_name='email_resets')
    new_email = models.CharField(max_length=50, blank=True,
                                 verbose_name=u'New Email')
    key = models.CharField(max_length=200, unique=True, db_index=True)
    is_active = models.BooleanField(default=False)

    objects = ResetEmailManager()


class BlackList(models.Model):
    """
        Model for storing bounced and complained emails of amazon
    """
    email = models.EmailField(max_length=100, unique=True, blank=False,
                              null=False, verbose_name=u'email')
    is_bounced = models.BooleanField(default=False)
    is_complained = models.BooleanField(default=False)
