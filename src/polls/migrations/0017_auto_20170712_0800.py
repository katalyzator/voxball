# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-12 08:00
from __future__ import unicode_literals

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0016_merge_20170628_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='title_sv',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='poll',
            index=django.contrib.postgres.indexes.GinIndex(fields=[b'title_sv'], name='polls_poll_title_s_ca66b1_gin'),
        ),
    ]
