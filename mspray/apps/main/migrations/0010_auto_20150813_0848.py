# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20150812_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='code',
            field=models.CharField(db_index=1, max_length=255),
        ),
    ]
