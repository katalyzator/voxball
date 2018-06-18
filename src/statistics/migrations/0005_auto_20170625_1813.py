# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-25 18:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0004_userstat_is_viewed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userstat',
            name='is_viewed',
        ),
        migrations.AddField(
            model_name='userstat',
            name='poll_answered',
            field=models.BooleanField(default=False, verbose_name='\u041e\u0442\u0432\u0435\u0447\u0435\u043d'),
        ),
        migrations.AddField(
            model_name='userstat',
            name='poll_created',
            field=models.BooleanField(default=False, verbose_name='\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043e\u043f\u0440\u043e\u0441\u0430'),
        ),
        migrations.AddField(
            model_name='userstat',
            name='poll_viewed',
            field=models.BooleanField(default=False, verbose_name='\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u043d'),
        ),
        migrations.AddField(
            model_name='userstat',
            name='user',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AddField(
            model_name='userstat',
            name='user_created',
            field=models.BooleanField(default=False, verbose_name='\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f'),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='poll',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='polls.Poll'),
        ),
    ]
