# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-18 12:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0009_userstat_widget'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstat',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 9, 18, 12, 17, 6, 105202, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
