# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-05 08:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0037_auto_20171205_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainuser',
            name='partner_type',
            field=models.PositiveIntegerField(default=0, verbose_name='\u0422\u0438\u043f \u043f\u0440\u043e\u0444\u0438\u043b\u044f \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0430'),
        ),
    ]
