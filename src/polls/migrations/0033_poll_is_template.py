# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-13 16:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0032_auto_20170813_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='is_template',
            field=models.BooleanField(db_index=True, default=False, verbose_name='\u0428\u0430\u0431\u043b\u043e\u043d?'),
        ),
    ]
