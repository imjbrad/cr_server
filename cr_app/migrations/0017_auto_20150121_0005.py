# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0016_crinsightchoice_choice_display_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crinsightchoice',
            name='choice_display_name',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
    ]
