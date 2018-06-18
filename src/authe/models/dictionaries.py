# -*- coding: utf-8 -*-
from django.db import models


class Country(models.Model):
    """
    Reference model for Countries
    """
    name = models.CharField(max_length=100, verbose_name=u'Название')
    code = models.CharField(max_length=100, verbose_name=u'Код', default='',
                            unique=True)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def full(self):
        return {
            'id': self.pk,
            'name': self.name,
            'code': self.code
        }

    class Meta:
        unique_together = ('name', 'code')
        verbose_name_plural = u"Страна"
        verbose_name = u"Страна"


class City(models.Model):
    """
    Reference model of City
    """
    name = models.CharField(max_length=100, verbose_name=u'Название')
    country = models.ForeignKey(Country, related_name='countries')

    def full(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country.full()
        }

    def short(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'country')
        verbose_name_plural = u"Города"
        verbose_name = u"Город"


class AppVersion(models.Model):
    """
    Reference model for ios&android version storing
    """
    ios_verion = models.CharField(max_length=100, verbose_name=u'Версия iOS')
    and_verion = models.CharField(max_length=100, verbose_name=u'Версия And')

    def __unicode__(self):
        return self.ios_verion

    def full(self):
        return {
            'ios_verion': self.ios_verion,
            'and_verion': self.and_verion
        }

    class Meta:
        verbose_name_plural = u"Версии приложений"
        verbose_name = u"Версия приложения"

