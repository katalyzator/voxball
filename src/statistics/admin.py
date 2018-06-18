# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from statistics.models import UserStat


@admin.register(UserStat)
class UserStat(admin.ModelAdmin):
    list_display = ('id', 'poll', 'user', 'poll_created', 'poll_answered',
                    'poll_viewed')
    list_filter = ('poll_answered', 'poll_created',
                   'poll_viewed', 'user_created', 'widget')

    search_fields = ['poll__id']
