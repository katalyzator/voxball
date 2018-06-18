# -*- coding: utf-8 -*-
from django.contrib import admin

from polls.models import Poll, PollChoice, PollAnswer, Keyword, PollKeyword, \
    PollCategory, Category, UserCategory

from polls.models import PollComment


class PollChoiceAdmin(admin.TabularInline):
    model = PollChoice
    list_display = ('id',
                    'poll',
                    'sc_value',
                    'rs_value',
                    'is_active',
                    'priority',
                    'timestamp')
    search_fields = ['=poll__id', '=poll__title']
    readonly_fields = ['answered_count']


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'title',
                    'date_begin',
                    'date_end',
                    'paid',
                    'poll_type',
                    'private_code',
                    'slug')
    inlines = [PollChoiceAdmin]
    search_fields = ['=user__id', '=user__email', '=user__phone']
    # readonly_fields = ['date_begin', 'date_end', 'rank']


@admin.register(PollAnswer)
class PollAnswerAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'user_cookie',
                    'poll',
                    'poll_choice',
                    'agent',
                    'referer',
                    'location',
                    'location_ip',
                    'location_country',
                    'location_region',
                    'location_city',
                    'source')
    search_fields = ['=poll__id', '=poll__title']
    readonly_fields = ['timestamp']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category')


@admin.register(PollCategory)
class PollCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'poll')
    search_fields = ['=poll__id']


@admin.register(PollKeyword)
class PollKeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'keyword', 'poll')
    search_fields = ['=poll__id']


@admin.register(UserCategory)
class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'count', 'is_active')


@admin.register(PollComment)
class PollCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'poll', 'comment')
    search_fields = ['=poll_id']
