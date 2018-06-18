# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-24 06:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0036_auto_20170823_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='privacy_type',
            field=models.SmallIntegerField(choices=[(0, 'Public'), (1, 'Private')], db_index=True, default=0, verbose_name='\u041f\u0443\u0431\u043b\u0438\u0447\u043d\u043e\u0441\u0442\u044c'),
        ),
        migrations.AddField(
            model_name='poll',
            name='private_code',
            field=models.CharField(blank=True, max_length=200, verbose_name='\u041f\u0440\u0438\u0432\u0430\u0442\u043d\u044b\u0439 \u043a\u043b\u044e\u0447'),
        ),
    ]
