# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-22 09:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0014_poll_keywords_array'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercategory',
            name='count',
            field=models.PositiveIntegerField(default=0, verbose_name='\u041d\u043e\u0432\u044b\u0445 \u043f\u043e\u0441\u0442\u043e\u0432'),
        ),
    ]
