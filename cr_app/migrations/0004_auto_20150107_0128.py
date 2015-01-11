# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0003_auto_20150106_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='insight_votes',
            field=jsonfield.fields.JSONField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='vote',
            name='choice',
            field=models.ForeignKey(related_name='votes', to='cr_app.CRInsightChoice'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='insight',
            field=models.ForeignKey(related_name='votes', to='cr_app.CRInsight'),
            preserve_default=True,
        ),
    ]
