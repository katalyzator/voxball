# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-12 14:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0013_resetemailrequest'),
        ('polls', '0030_auto_20170811_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authe.City', verbose_name='\u0413\u043e\u0440\u043e\u0434 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f'),
        ),
    ]
