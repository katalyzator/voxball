# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-02 12:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderators', '0008_article_title'),
        ('statistics', '0007_remove_userstat_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstat',
            name='article',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='moderators.Article'),
        ),
    ]