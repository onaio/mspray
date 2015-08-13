# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20150813_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='houses',
            field=models.IntegerField(default=0, db_index=1),
        ),
        migrations.AlterField(
            model_name='targetarea',
            name='targetid',
            field=models.CharField(max_length=254, unique=True, db_index=1),
        ),
    ]
