# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-06 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0044_poll_partner_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='partner_author',
            field=models.CharField(default=b'', max_length=250, verbose_name='\u0410\u0432\u0442\u043e\u0440 \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0430'),
        ),
    ]
