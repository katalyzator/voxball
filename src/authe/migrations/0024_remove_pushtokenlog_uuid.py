# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-11 09:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0023_auto_20170908_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pushtokenlog',
            name='uuid',
        ),
    ]
