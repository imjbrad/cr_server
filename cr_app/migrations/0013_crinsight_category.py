# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0012_upvote'),
    ]

    operations = [
        migrations.AddField(
            model_name='crinsight',
            name='category',
            field=models.CharField(default='ov', max_length=160, choices=[(b'ov', b'OVERALL'), (b'ov', b'TOP')]),
            preserve_default=False,
        ),
    ]
