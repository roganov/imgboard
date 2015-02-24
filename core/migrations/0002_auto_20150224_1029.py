# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='title',
            field=models.CharField(default='Title', max_length=150),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='thread',
            name='board',
            field=models.ForeignKey(to='core.Board', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='thread',
            index_together=set([('board', 'is_pinned', 'bumped_at')]),
        ),
    ]
