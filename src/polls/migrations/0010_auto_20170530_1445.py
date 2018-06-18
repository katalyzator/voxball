# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-30 14:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0009_auto_20170530_1445'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='usercategories',
            index_together=set([('user', 'category')]),
        ),
    ]
