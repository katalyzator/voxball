# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-13 16:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0015_mainuser_repost_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainuser',
            name='repost_count',
            field=models.IntegerField(default=0, verbose_name='\u041a\u043e\u043b-\u0432\u043e \u0440\u0435\u043f\u043e\u0441\u0442\u043e\u0432'),
        ),
    ]
