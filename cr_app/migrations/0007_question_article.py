# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0006_auto_20150107_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='article',
            field=models.ForeignKey(related_name='questions', default=1, to='cr_app.Article'),
            preserve_default=False,
        ),
    ]
