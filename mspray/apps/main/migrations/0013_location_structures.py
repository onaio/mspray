# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='structures',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
