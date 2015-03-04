# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150225_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='raw_body',
            field=models.TextField(validators=[django.core.validators.RegexValidator(regex=b'^\\s*$', message=b'The body may not be empty.', inverse_match=True)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=b'thumbs/'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thread',
            name='raw_body',
            field=models.TextField(validators=[django.core.validators.RegexValidator(regex=b'^\\s*$', message=b'The body may not be empty.', inverse_match=True)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thread',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=b'thumbs/'),
            preserve_default=True,
        ),
    ]
