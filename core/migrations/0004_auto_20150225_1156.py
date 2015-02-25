# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150224_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=b'/thumbs/'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=b'/thumbs/'),
            preserve_default=True,
        ),
    ]
