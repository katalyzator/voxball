# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-15 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstat',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userstat',
            name='country',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userstat',
            name='region',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
