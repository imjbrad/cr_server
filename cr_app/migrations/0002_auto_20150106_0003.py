# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cr_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='publisher',
            new_name='publishers',
        ),
    ]
