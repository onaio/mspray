# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_auto_20151019_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprayday',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='sprayday',
            name='start_time',
            field=models.DateTimeField(null=True),
        ),
    ]
