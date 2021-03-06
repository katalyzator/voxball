# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 14:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, unique=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '\u041a\u043b\u044e\u0447\u0435\u0432\u043e\u0435 \u0441\u043b\u043e\u0432\u043e',
                'verbose_name_plural': '\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u0441\u043b\u043e\u0432\u0430',
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=1000, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('image', models.ImageField(blank=True, null=True, upload_to=b'poll_avatars', verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u043e\u043f\u0440\u043e\u0441\u0430')),
                ('timestamp', models.BigIntegerField(default=0, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f')),
                ('date_begin', models.BigIntegerField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u043e\u043f\u0440\u043e\u0441\u043d\u0438\u043a\u0430')),
                ('date_end', models.BigIntegerField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043e\u043f\u0440\u043e\u0441\u043d\u0438\u043a\u0430')),
                ('paid', models.BooleanField(default=False, verbose_name='\u041e\u043f\u043b\u0430\u0447\u0435\u043d\u043d\u044b\u0439 \u043e\u043f\u0440\u043e\u0441?')),
                ('min_value', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u041c\u0438\u043d \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u0434\u043b\u044f rating_scale')),
                ('max_value', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u041c\u0430\u043a\u0441 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u0434\u043b\u044f rating_scale')),
                ('is_active', models.BooleanField(default=True)),
                ('poll_type', models.SmallIntegerField(choices=[(0, 'rating scale'), (1, 'single choice'), (2, 'multiple choice')], default=1, verbose_name='\u0422\u0438\u043f \u043e\u043f\u0440\u043e\u0441\u0430')),
                ('total_answered_count', models.IntegerField(default=0, verbose_name='\u041e\u0431\u0449\u0435\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u0440\u043e\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u0432\u0448\u0438\u0445')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='polls', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u041e\u043f\u0440\u043e\u0441',
                'verbose_name_plural': '\u041e\u043f\u0440\u043e\u0441\u044b',
            },
        ),
        migrations.CreateModel(
            name='PollAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_cookie', models.CharField(blank=True, max_length=200, null=True, verbose_name=b'\xd0\xa1\xd0\xb3\xd0\xb5\xd0\xbd\xd0\xb5\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xba\xd1\x83\xd0\xba\xd0\xb8')),
                ('agent', models.CharField(blank=True, max_length=200, verbose_name='\u0410\u0433\u0435\u043d\u0442')),
                ('referer', models.CharField(blank=True, max_length=1000, verbose_name='\u0420\u0435\u0444\u0435\u0440\u0435\u043d\u0442')),
                ('location', models.CharField(max_length=200)),
                ('location_ip', models.CharField(blank=True, max_length=50, verbose_name='ip-\u0430\u0434\u0440\u0435\u0441')),
                ('location_country', models.CharField(blank=True, max_length=200, verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430')),
                ('location_region', models.CharField(blank=True, max_length=200, verbose_name='\u0420\u0435\u0433\u0438\u043e\u043d')),
                ('location_city', models.CharField(blank=True, max_length=200, verbose_name='\u0413\u043e\u0440\u043e\u0434')),
                ('source', models.SmallIntegerField(choices=[(0, '\u0411\u0440\u0430\u0443\u0437\u0435\u0440'), (1, 'iOS'), (2, '\u0410\u043d\u0434\u0440\u043e\u0438\u0434')], default=0, verbose_name='\u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a \u043e\u0442\u0432\u0435\u0442\u0430')),
                ('is_active', models.BooleanField(default=True)),
                ('timestamp', models.BigIntegerField(default=0)),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='polls.Poll')),
            ],
            options={
                'verbose_name': '\u041e\u0442\u0432\u0435\u0442 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f',
                'verbose_name_plural': '\u041e\u0442\u0432\u0435\u0442\u044b \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
            },
        ),
        migrations.CreateModel(
            name='PollChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sc_value', models.CharField(blank=True, max_length=200, verbose_name='\u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435 single_choice \u043e\u0442\u0432\u0435\u0442\u0430')),
                ('rs_value', models.SmallIntegerField(blank=True, default=0, verbose_name='\u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435 rating_scale \u043e\u0442\u0432\u0435\u0442\u0430')),
                ('is_active', models.BooleanField(default=True, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u044b\u0439?')),
                ('priority', models.SmallIntegerField(default=0, verbose_name='\u041f\u0440\u0438\u043e\u0440\u0438\u0442\u0435\u0442')),
                ('timestamp', models.BigIntegerField(default=0)),
                ('answered_count', models.IntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u0440\u043e\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u0432\u0448\u0438\u0445 \u0437\u0430 \u044d\u0442\u043e\u0442 \u043e\u0442\u0432\u0435\u0442')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='polls.Poll')),
            ],
            options={
                'verbose_name': '\u0412\u0430\u0440\u0438\u0430\u043d\u0442 \u043e\u0442\u0432\u0435\u0442\u0430',
                'verbose_name_plural': '\u0412\u0430\u0440\u0438\u0430\u043d\u0442\u044b \u043e\u0442\u0432\u0435\u0442\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='PollKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('timestamp', models.BigIntegerField(default=0)),
                ('keyword', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='polls.Keyword', verbose_name='\u0422\u0435\u0433')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='polls.Poll')),
            ],
            options={
                'verbose_name': '\u041a\u043b\u044e\u0447\u0435\u0432\u043e\u0435 \u0441\u043b\u043e\u0432\u043e \u043e\u043f\u0440\u043e\u0441\u0430',
                'verbose_name_plural': '\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u0441\u043b\u043e\u0432\u0430 \u043e\u043f\u0440\u043e\u0441\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='PollTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='polls.Poll')),
            ],
            options={
                'verbose_name': '\u041a\u043b\u044e\u0447\u0435\u0432\u043e\u0439 \u0442\u043e\u043f\u0438\u043a \u043e\u043f\u0440\u043e\u0441\u0430',
                'verbose_name_plural': '\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u0442\u043e\u043f\u0438\u043a\u0438 \u043e\u043f\u0440\u043e\u0441\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': '\u0422\u043e\u043f\u0438\u043a',
                'verbose_name_plural': '\u0422\u043e\u043f\u0438\u043a\u0438',
            },
        ),
        migrations.AddField(
            model_name='polltopic',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='polls', to='polls.Topic'),
        ),
        migrations.AddField(
            model_name='pollanswer',
            name='poll_choice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choice_answers', to='polls.PollChoice'),
        ),
        migrations.AddField(
            model_name='pollanswer',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='keyword',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='polls.Topic'),
        ),
    ]
