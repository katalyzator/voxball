# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-07 13:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0027_poll_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='rank',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
    ]
