# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-13 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0033_poll_is_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
