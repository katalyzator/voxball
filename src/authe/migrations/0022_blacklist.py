# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-08 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authe', '0021_auto_20170906_0734'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='email')),
                ('is_bounced', models.BooleanField(default=False)),
                ('is_complained', models.BooleanField(default=False)),
            ],
        ),
    ]