# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-14 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0008_userstat_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstat',
            name='widget',
            field=models.BooleanField(default=False, verbose_name='\u0412\u0438\u0434\u0436\u0435\u0442?'),
        ),
    ]