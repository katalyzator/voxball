# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from moderators.models import PollTemplate, PollChoiceTemplate, \
    PollTemplateCategory, Article, ArticlePollEntry


class PollChoiceTemplateAdmin(admin.TabularInline):
    model = PollChoiceTemplate
    list_display = ('id',
                    'poll',
                    'sc_value',
                    'rs_value',
                    'is_active',
                    'priority',
                    'timestamp')


@admin.register(PollTemplate)
class PollTemplateAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'title',
                    'date_begin',
                    'date_end',
                    'paid',
                    'poll_type',
                    'min_value',
                    'max_value')
    inlines = [PollChoiceTemplateAdmin]


@admin.register(PollTemplateCategory)
class PollTemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'poll')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'article_url', 'is_active')


@admin.register(ArticlePollEntry)
class ArticlePollEntryCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'poll')

    list_filter = ('article', )
