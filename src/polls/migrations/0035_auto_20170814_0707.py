# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-14 07:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0034_auto_20170813_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='timestamp',
            field=models.BigIntegerField(db_index=True, default=0, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f'),
        ),
    ]
