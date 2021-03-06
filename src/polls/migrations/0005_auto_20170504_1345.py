# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 13:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='polls', to='polls.Category')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='polls.Poll')),
            ],
            options={
                'verbose_name': '\u041a\u043b\u044e\u0447\u0435\u0432\u0430\u044f \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u043e\u043f\u0440\u043e\u0441\u0430',
                'verbose_name_plural': '\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 \u043e\u043f\u0440\u043e\u0441\u043e\u0432',
            },
        ),
        migrations.AddField(
            model_name='keyword',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='polls.Category'),
        ),
    ]
