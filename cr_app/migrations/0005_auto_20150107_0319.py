# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0004_auto_20150107_0128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(related_name='articles', to='cr_app.Author'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='insight_votes',
            field=jsonfield.fields.JSONField(default=b'{}'),
            preserve_default=True,
        ),
    ]
