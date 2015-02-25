# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150224_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.image_upload_path),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.image_upload_path),
            preserve_default=True,
        ),
    ]
