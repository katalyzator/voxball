# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 15:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20170503_1536'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pollkeyword',
            old_name='poll_keyword',
            new_name='keyword',
        ),
    ]