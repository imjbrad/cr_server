# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0013_crinsight_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='insight_votes',
            field=jsonfield.fields.JSONCharField(default={}, max_length=5000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='crinsight',
            name='category',
            field=models.CharField(max_length=160, choices=[(b'ov', b'OVERALL'), (b'top', b'TOP')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='upvotes',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
