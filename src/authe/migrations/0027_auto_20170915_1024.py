# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-15 10:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0026_mainuser_push'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainuser',
            name='push',
            field=models.BooleanField(default=True, verbose_name='Push \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f'),
        ),
    ]
