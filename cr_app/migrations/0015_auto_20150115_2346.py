# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0014_auto_20150115_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='insight_votes',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=True,
        ),
    ]
