# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-20 14:48
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0013_auto_20170610_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='keywords_array',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), default=[], size=None, verbose_name='\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u0441\u043b\u043e\u0432\u0430'),
        ),
    ]
