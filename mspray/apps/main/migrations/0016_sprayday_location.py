# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20150831_0711'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprayday',
            name='location',
            field=models.ForeignKey(default=2, to='main.Location'),
        ),
    ]
