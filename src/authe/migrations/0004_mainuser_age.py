# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-30 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0003_activation_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainuser',
            name='age',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0412\u043e\u0437\u0440\u0430\u0441\u0442'),
        ),
    ]
