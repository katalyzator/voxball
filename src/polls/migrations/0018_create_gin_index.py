# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-12 09:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0017_auto_20170712_0800'),
    ]

    operations = [
        migrations.RunSQL(                                                                                                                                                                                          
            "CREATE INDEX test_idx ON polls_poll USING GIN (to_tsvector('english', title))"
        )
    ]
