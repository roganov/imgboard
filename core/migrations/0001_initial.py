# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True)),
                ('threads_per_page', models.PositiveSmallIntegerField(default=10)),
                ('pages_num', models.PositiveSmallIntegerField(default=10)),
                ('bumplimit', models.PositiveSmallIntegerField(default=500)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('title', models.CharField(max_length=150, blank=True)),
                ('raw_body', models.TextField()),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_hidden', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('title', models.CharField(max_length=150, blank=True)),
                ('raw_body', models.TextField()),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('is_pinned', models.BooleanField(default=False)),
                ('is_closed', models.BooleanField(default=False, help_text=b'New posts cannot be submitted.')),
                ('posts_count', models.IntegerField(default=0)),
                ('bumped_at', models.DateTimeField(auto_now_add=True)),
                ('board', models.ForeignKey(to='core.Board')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(to='core.Thread'),
            preserve_default=True,
        ),
    ]
