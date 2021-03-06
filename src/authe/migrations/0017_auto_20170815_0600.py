# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-15 06:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0016_auto_20170813_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainuser',
            name='avatar_height',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mainuser',
            name='avatar_width',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='mainuser',
            name='avatar',
            field=models.ImageField(blank=True, height_field=b'avatar_height', null=True, upload_to=b'user_avatars', width_field=b'avatar_width'),
        ),
    ]
