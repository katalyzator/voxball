# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-03 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0011_auto_20170703_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(default=b'', max_length=100, unique=True, verbose_name='\u041a\u043e\u0434'),
        ),
    ]
