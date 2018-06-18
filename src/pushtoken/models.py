# -*- coding: utf-8 -*-

from django.db import models


class PushSender(models.Model):
    title = models.CharField(max_length=1000, verbose_name=u"Заголовок",
                             db_index=True)
    url = models.CharField(max_length=1000, verbose_name=u"Заголовок",
                             db_index=True)
    sent = models.BooleanField(default=False, db_index=True)
    added = models.TimeField(auto_now_add=True)
