# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0002_auto_20150106_0003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='author',
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='cr_app.Author'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='article',
            name='publisher',
            field=models.ForeignKey(related_name='articles', to='cr_app.Publisher'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='article',
            field=models.ForeignKey(related_name='votes', to='cr_app.Article'),
            preserve_default=True,
        ),
    ]
